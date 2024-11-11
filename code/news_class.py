from langchain.chains import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.messages import AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate
from langchain_community.vectorstores import Qdrant
from document import Document
import datetime
import json
import re
import redis
import random
from sentence_transformers import SentenceTransformer, util
class LunyuQASystem:
    """
    论语问答系统类
    实现基于角色的问答功能，使用LangChain进行RAG（检索增强生成）
    
    主要功能：
    1. 加载并处理问题和话题数据
    2. 为每个角色建立向量知识库
    3. 生成符合角色特征的回答
    4. 将结果存储到Redis数据库
    """

    def __init__(self, model_name="Lunyu"):
        """
        初始化问答系统
        
        Args:
            model_name (str): 使用的LLM模型名称
            redis_db (int): Redis数据库编号
        """
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_model(model_name)
        self.setup_redis()
        self.setup_output_parser()
        self.news_answer=[]
        self.model= SentenceTransformer("model/embedding/m3e-base")
        self.id=0

    def setup_model(self, model_name):
        """
        设置LLM模型和embeddings
        """
        self.chat_model = ChatOllama(model=model_name)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="model/embedding/m3e-base",
            model_kwargs={"device": "cpu"}
        )

    def setup_redis(self):
        """
        设置Redis连接,
        这里设置两个不同的redis缓存位置
        分别为db5和db7
        db5:全角色QA数据
        db7:新闻数据
        """
        self.redis_client_db5 = redis.StrictRedis(
            host="localhost",
            port=6379,
            db=5,
            decode_responses=True
        )
        self.redis_client_db7 = redis.StrictRedis(
            host="localhost",
            port=6379,
            db=7,
            decode_responses=True
        )

    def setup_output_parser(self):
        """
        设置输出解析器，定义回答的格式
        """
        response_schema = [
            ResponseSchema(
                name="answer",
                description="用论语的文言文文风回答, 局内标点符号用中文全角"
            ),
            ResponseSchema(
                name="answer_translation",
                description="上述论语文言文回答的现代文翻译, 局内标点符号用中文全角"
            )
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schema)

    def insert__news_answer_data_redis(self, result):
        """
        将问答结果插入Redis数据库
        """
        r = redis.StrictRedis(host="localhost", port=6379, db=7, decode_responses=True)

        self.id+=1
        r.hset(
            self.id,
            mapping={
                "answer_part":result["answer_part"],
                "answer_translation":result["answer_translation"],
                "role":result["role"],
                "title":result["title"]

            }
        )
        print(f"Data inserted with ID: {id}")

    def create_retrieval_chains(self, role_docs):
        """
        创建检索链和文档链
        
        Args:
            role_docs (list): 角色相关文档列表
        Returns:
            retriever_chain: 完整的检索链
        """
        # 创建向量存储
        vector = Qdrant.from_documents(
            documents=role_docs,
            embedding=self.embeddings,
            location=":memory:",
            collection_name="preload_docs"
        )
        
        # 设置检索器
        vector_retriever = vector.as_retriever()
        
        # 创建历史感知检索链
        history_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "需求的描述是{input}"),
            ("user", "Given the introduction in docs, generate answer in corresponding view")
        ])
        
        history_chain = create_history_aware_retriever(
            llm=self.chat_model,
            prompt=history_prompt,
            retriever=vector_retriever
        )
        
        # 创建文档链
        doc_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            你现在是孔子门徒，
            你会根据你的人物事迹和性格特征，对事物发表你的看法。
            现在我会与你对话，请你用《论语》中文言文风格与我交流
            {context}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}")
        ])
        
        documents_chain = create_stuff_documents_chain(self.chat_model, doc_prompt)
        return create_retrieval_chain(history_chain, documents_chain)

    def process_model_output(self, content):
        """
        处理模型输出，提取答案和翻译
        
        Args:
            content (str): 模型原始输出
        Returns:
            tuple: (answer_part, answer_translation)
        """
        json_str = content.strip("```json\n").strip("```")
        content_processed = re.sub(r'[{}""" ]+', "", json_str)
        
        # 提取答案部分
        start_index = content_processed.find("answer:") + len("answer:")
        end_index = content_processed.find("answer_translation:")
        answer_part = content_processed[start_index:end_index].strip()
        
        # 提取翻译部分
        start_index_translation = content_processed.find("answer_translation:") + len("answer_translation:")
        answer_translation = content_processed[start_index_translation:].strip()
        
        return answer_part, answer_translation

    def generate_role_answer(self, role,news_title, news_topic,news_snippet, dialog, role_info):
        """
        为特定角色生成答案
        
        Args:
            topic (str): 主题
            title (str): 事件标题
            snippet (str): 事件简介
            role (str): 角色名称
            dialog (str): 角色相关对话
            role_info (dict): 角色信息
        """
        # 准备角色文档
        docs_preload = [
            Document(page_content=str(role_info["story"]), metadata={"label": "role_overview"}),
            Document(page_content=str(role_info["comments"]), metadata={"label": "role_comments"})
        ]
        
        # 创建检索链
        retriever_chain = self.create_retrieval_chains(docs_preload)
        
        # 准备提示
        role_prompt = f"""
        现在讨论的主题为：{news_topic},
        现在有这样一个热点事件：{news_title},
        事件具体内容为：{news_snippet}
        论语中人物：{role},
        曾经对这个主题题发表过见解：{dialog}
        请用你的风格与我对话，发表你对该热点事件的见解！！！
        """
        
        input_str = f"""
        {role_prompt}\n
        please strictly answer in format: 
        {self.output_parser.get_format_instructions()}
        """
        
        # 获取答案
        output_completion = retriever_chain.invoke({
            "input": input_str,
            "chat_history": []
        })
        
        # 处理输出
        answer_part, answer_translation = self.process_model_output(output_completion["answer"])

        # 返回结果
        result={
            "answer_part":answer_part,
            "answer_translation":answer_translation,
            "role":role,
            "title":news_title
        }
        # 将数据插入数据库
        self.insert__news_answer_data_redis(result=result)
        return result


        
       

    def process_news_data(self, informations_from_front,role_file_path="data/role.json"):
        # 初始化回答列表
        self.news_answer=[]
        """
        处理问答数据的主要方法
        
        Args:
            informations_from_front:前端传递过来的新闻信息
            role_file_path (str): 角色数据文件路径
            
        """
        # 解析informations_from_front
        news_title = informations_from_front["title"]
        news_topic=informations_from_front["theme"]
        news_snippet = informations_from_front["snippet"]

        print("Title:", news_title)
        print("Theme:", news_topic)
        print("Snippet:", news_snippet)
        # 列出 Redis_db5 中的所有哈希键
        keys =self.redis_client_db5.keys('*')
        
        # 加载角色数据
        with open(role_file_path, "r", encoding="utf-8") as file:
            role_data = json.load(file)
      

        for key in keys:
            # 获取每个哈希键的 'topic' 字段
            topic_from_front = self.redis_client_db5.hget(key, 'topic')

            if topic_from_front:
                if isinstance(topic_from_front, bytes):
                    topic_from_front = topic_from_front.decode('utf-8')
                print(f"当前键 {key} 的 topic 是: {topic_from_front}")
               
                # 如果 'topic' 字段的值与传入的 topic_from_front 匹配
                if topic_from_front.strip() == news_topic.strip():
                    print("相等")
                    # 处理角色信息
                    role=self.redis_client_db5.hget(key,'role')
                    dialog=self.redis_client_db5.hget(key,'dialog')
                    # 查找角色信息
                    role_info = next(
                        (item for item in role_data if item["name"] == role),
                        None
                    )
                    
                    if role_info:
                        result=self.generate_role_answer(
                            role,news_title, news_topic,news_snippet,dialog, role_info
                        )    
                        
                        self.news_answer.append(result)
                        print(result,"\n");  
                        
    def similarity_news_match(self,answer_from_front,informations_from_front):
        """
            新闻相似度匹配
            answer_from_front:前端返回的回答
        """
        print(f"Received answer from front: {answer_from_front} ")
        # 解析informations_from_front
        news_title = informations_from_front["title"]
        news_topic=informations_from_front["theme"]
        news_snippet = informations_from_front["snippet"]
        # 直接从 Redis_db7 中获取所有哈希键,如果没有，则在线生成答案
        keys = self.redis_client_db7.keys('*')

        

        library_answer_translations = []  # 用于存储答案的翻译
        library_answers = []  # 用于存储原始答案
        roles = []  # 存储对应的回答者
        key_mappings = []  # 存储键名，便于在相似度最高时查找
        if not keys:
            # 在线生成
            print("Redis 中没有找到任何匹配的键。开始在线生成")
            self.process_news_data(informations_from_front=informations_from_front)
            for item in self.news_answer:
                library_answers.append(item["answer_part"])
                library_answer_translations.append(item["answer_translation"])
                roles.append(item["role"])
                

            
        else:
            # 直接在数据库中获取
            print("直接在数据库中获取")
            for key in keys:
                title=self.redis_client_db7.hget(key,'title')
                answer_part = self.redis_client_db7.hget(key, 'answer_part')
                answer_translation = self.redis_client_db7.hget(key, 'answer_translation')
                role = self.redis_client_db7.hget(key, 'role')
                
                if title and answer_part and answer_translation and role:
                    if isinstance(title, bytes):
                        title = title.decode('utf-8')
                    if title == news_title:
                        if isinstance(role, bytes):
                            role = role.decode('utf-8')
                        print("角色：",role)
                        if isinstance(answer_part, bytes):
                            answer_part = answer_part.decode('utf-8')
                        print("回答：",answer_part)
                        if isinstance(answer_translation, bytes):
                            answer_translation = answer_translation.decode('utf-8')
                        library_answers.append(answer_part)
                        library_answer_translations.append(answer_translation)
                        roles.append(role)
                        key_mappings.append(key)

        if not library_answer_translations:
            print(f"没有找到与主题 {news_title} 匹配的答案翻译。")
            return None

        # 对前端传来的回答进行编码
        embedding_front_answer = self.model.encode(answer_from_front)
        # 对筛选出的答案翻译进行编码
        embeddings_library_answer_translations = self.model.encode(library_answer_translations)
        
        # 计算前端回答与库中所有筛选出的答案翻译的余弦相似度
        cosine_similarities = util.pytorch_cos_sim(embedding_front_answer, embeddings_library_answer_translations).flatten()
        print(f"Cosine similarities: {cosine_similarities}")
        
        # 找出相似度最高的答案索引（随机打破平局）
        max_similarity = cosine_similarities.max().item()
        most_similar_indices = [i for i, similarity in enumerate(cosine_similarities) if similarity == max_similarity]
        most_similar_index = random.choice(most_similar_indices)
        
        # 返回与相似度最高的原始答案和对应的角色
        most_similar_answer = library_answers[most_similar_index]
        corresponding_role = roles[most_similar_index]
        most_similar_answer_trans = library_answer_translations[most_similar_index]
        print(f"Most similar answer: {most_similar_answer}")
        print(f"Role: {corresponding_role}")
        
        return {
            "answer": most_similar_answer,
            "answer_translation":most_similar_answer_trans,
            "role": corresponding_role
        }
# lunyu=LunyuQASystem()
# information=  {
#         "title": "沧州经济开发区：传承孝道 情暖重阳",
#         "link": "http://he.people.com.cn/n2/2024/1010/c192235-41003197.html",
#         "snippet": "10月10日，河北省沧州市兴业路小学的学生们走进沧州经济开发区雅布伦养老院，开展“感恩重阳老幼同乐”重阳节慰问活动，为老人们送上关怀和节日的祝福。",
#         "date": "3 days ago",
#         "source": "人民网",
#         "theme": "孝道的理解",
#         "img_url":"http://he.people.com.cn/NMediaFile/2024/1010/LOCAL1728552317000FDYOUTP0QW.jpg"

# }
# lunyu.process_news_data(informations_from_front=information)