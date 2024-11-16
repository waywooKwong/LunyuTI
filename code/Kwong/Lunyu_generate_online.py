# -*- coding: utf-8 -*-
"""
20/10/2024 本代码预留 FastAPI 接口供前端在线调用模型生成
    注意具体的参数需求
    
"""

"""
PostMan 使用教程：

在 Postman 中模拟请求到 FastAPI，可以按照以下步骤进行：

### 步骤1: 打开 Postman

确保已经安装并打开了 Postman。可以从 [Postman官网](https://www.postman.com/downloads/)下载并安装。

### 步骤2: 创建新的请求

1. 点击 **"New"** 按钮，选择 **"Request"**。
2. 为请求命名，并选择一个已经存在或创建一个新的 **Collection** 来保存请求。
3. 点击 **"Create"** 按钮。

### 步骤3: 设置请求类型和 URL

1. 将请求类型设置为 **POST**。
2. 在 **URL** 栏中输入 FastAPI 服务的地址，假设你在本地运行，地址将是：
   ```
   http://localhost:9090/Lunyu_generate/
   ```

### 步骤4: 配置请求头

1. 点击 **"Headers"** 选项卡。
2. 添加一个新的 Header：
   - **Key**: `Content-Type`
   - **Value**: `application/json`

### 步骤5: 编写请求体

1. 点击 **"Body"** 选项卡。
2. 选择 **"raw"** 作为 Body 的类型。
3. 选择 **JSON** 格式，并在文本框中输入你希望发送的数据。例如：

注意：这里 mode 参数可为空, 默认是None, 默认是角色回答问题
    如果 mode 设置为 "custom" , 是把角色的话翻译为古文
   ```json
   {
     "topic": "仁",
     "role": "邝伟华",
     "question": "学习有什么用",
     "dialog": "曾经谈到仁的价值",
     "mode": "custom" / None
   }
   ```

### 步骤6: 发送请求

1. 点击 **"Send"** 按钮。
2. Postman 将向 FastAPI 服务器发送请求，并返回结果。你可以在 **"Response"** 部分看到 FastAPI 返回的结果，例如：

   ```json
   {
     "answer": "生成的古文回答",
     "translation": "古文的现代文翻译"
   }
   ```

### 示例总结

- 请求类型：`POST`
- URL: `http://localhost:9090/Lunyu_generate/`
- Headers: `Content-Type: application/json`
- Body:
  ```json
  {
    "topic": "仁",
    "role": "邝伟华",
    "question": "学习有什么用",
    "dialog": "曾经谈到仁的价值",
    "mode": "custom" / None 
  }
  ```

通过上述操作，你可以在 Postman 中成功发送请求并接收 FastAPI 的响应。
"""

import random
from sentence_transformers import SentenceTransformer, util
from langchain.chains import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.messages import AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import (
    MessagesPlaceholder,
    ChatPromptTemplate,
    PromptTemplate,
)
import redis
# import datetime
# # 标记时间戳，便于文件命名于标定时间
# timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# import torch
# if torch.cuda.is_available():
#     print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
# else:
#     print("CUDA is not available. Falling back to CPU.")
# 数据库
redis_client_db5 = redis.StrictRedis(
            host="localhost",
            port=6379,
            db=5,
            decode_responses=True
 )
def online_generate(topic, role, question, dialog, mode,news_title=None,news_snippet=None):
    """
    args:
        topic: 谈论主题
        role: 当前角色
        question: 当前问题
        (optional) dialog: 角色对当前问题发表过什么见解
        (optional) mode: 函数的模式, None(默认,角色回答问题)/ custom (翻译成古文)
    return:
        answer_part: 模型生成的古文回答
        answer_translation: 古文的现代文翻译回答
    """

    # 出于参数调整的方便，我把 prompt 放到最前面
    if mode == "custom":  # mode 设置为 custom 整体函数用作把现代文翻译成古文
        prompt = f"""  
        {dialog}
        """

        role_prompt = f"""
        请把下述现代文翻译成论语风格：{prompt}
        """
    elif mode == "news":
        prompt = f"""
        现在讨论的主题为：{topic},
        现在有这样一个热点事件：{news_title},
        事件具体内容为：{news_snippet}
        论语中人物：{role},
        曾经对这个主题题发表过见解：{dialog}
        曾经对这个话题发表过见解：{dialog}
        """

        role_prompt = f"""
        你目前的角色设定是：{prompt}
        请用你的风格与我对话，发表你对问题的见解
        """
    else:
        prompt = f"""
        现在讨论的主题为：{topic},
        有人提出这样一个问题：{question},
        论语中人物：{role},
        曾经对这个话题发表过见解：{dialog}
        """

        role_prompt = f"""
        你目前的角色设定是：{prompt}
        请用你的风格与我对话，发表你对问题的见解
        """
    print("role_prompt:", role_prompt)

    ## 1.1 设定选择模型，这里使用 ChatOllama
    from langchain_community.chat_models import ChatOllama

    model_name = "Lunyu"  # 这里的 Lunyu 模型是 Ollama 基于 Qwen2.5 生成的
    chat_model = ChatOllama(model=model_name, device="cuda")

    ## 1.2 embeddings 模型（用 m3e-base），需要本地加载,，gitignore掉了
    from langchain_huggingface import HuggingFaceEmbeddings

    # 这里先确认模型有没有加载到本地
    embeddings = HuggingFaceEmbeddings(
        model_name="model\embedding\m3e-base", model_kwargs={"device": "cpu"}
    )
    print("embedding loading:", embeddings.model_name)

    # 分角色加载内容
    ## 1.3 向量库加载
    # retriever链中预加载的文本

    from document import Document
    from langchain_community.vectorstores import Qdrant
    import json
    import re

    docs_preload = []

    docs_preload.append(
        Document(
            page_content=str("hello"),
            metadata={"label": "role_overview"},
        )
    )
    docs_preload.append(
        Document(
            page_content=str("hello"),
            metadata={"label": "role_comments"},
        )
    )

    # 向量库加载角色信息的描述
    vector = Qdrant.from_documents(
        documents=docs_preload,
        embedding=embeddings,
        location=":memory:",
        collection_name="preload_docs",
    )

    vector_retriever = vector.as_retriever()

    history_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        messages=[
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", """需求的描述是{input}"""),
            (
                "user",
                "Given the introduction in docs, generate answer in corresponding view",
            ),
        ]
    )
    history_chain = create_history_aware_retriever(
        llm=chat_model,
        prompt=history_prompt,
        retriever=vector_retriever,
    )

    doc_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
            你现在是孔子门徒，\n
            你会根据你的人物事迹和性格特征，对事物发表你的看法。\n
            现在我会与你对话，请你用《论语》中文言文风格与我交流\n
            {context}
            """,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )
    documents_chain = create_stuff_documents_chain(chat_model, doc_prompt)
    retriever_chain = create_retrieval_chain(history_chain, documents_chain)

    chat_history = []

    # 特定的输出格式字符串
    input_str = """
    {role_prompt}\n

    please strictly answer in format: 
    {format_instruction}
    """

    from langchain.output_parsers import (
        ResponseSchema,
        StructuredOutputParser,
    )
    from langchain_core.prompts import PromptTemplate

    response_schema = [
        ResponseSchema(
            name="answer",
            description="用论语的文言文文风回答, 局内标点符号用中文全角",
        ),
        ResponseSchema(
            name="answer_translation",
            description="上述论语文言文回答的现代文翻译, 局内标点符号用中文全角",
        ),
    ]

    output_parser = StructuredOutputParser.from_response_schemas(
        response_schemas=response_schema
    )

    format_instruction = output_parser.get_format_instructions()
    prompt_template = PromptTemplate.from_template(
        template=input_str,
        partial_variables={"format_instruction": format_instruction},
    )

    prompt_str_input = prompt_template.format(role_prompt=role_prompt)
    output_completion: AIMessage = retriever_chain.invoke(
        {"input": prompt_str_input, "chat_history": chat_history}
    )
    content = output_completion["answer"]
    # print("generating answer:", content)

    # 去除开头和结尾的代码块标记
    json_str = content.strip("```json\n").strip("```")
    # print("json_str:", json_str)

    # 删除 {""}
    content_processed = re.sub(r'[{}"“” ]+', "", json_str)  # 删除 '{' 和 '"' 符号
    # print("cleaned_data:", content_processed)

    # 提取 answer: 后面到 answer_translation: 之间的内容
    start_index = content_processed.find("answer:") + len("answer:")
    end_index = content_processed.find("answer_translation:")
    answer_part = content_processed[start_index:end_index].strip()  # 去掉前后空格

    # 提取 answer_translation: 后的内容
    start_index_translation = content_processed.find("answer_translation:") + len(
        "answer_translation:"
    )
    answer_translation = content_processed[
        start_index_translation:
    ].strip()  # 去掉前后空格

    print("Answer Part:", answer_part)
    print("Answer Translation:", answer_translation)
     # 返回结果
    result={
        "answer_part":answer_part,
        "answer_translation":answer_translation,
        "role":role,
    }
    return result
"""
前端传递给后端的数据：
1.0 新闻：
information:{
    topic:主题,
    news_topic:新闻标题,
    news_snippet：新闻简介
    user_answer:用户对新闻的看法（用于相似度匹配）,
    mode:news

}
2.0 自定义问题

information:{
    topic:主题,
    question:自定义问题,
    user_answer:用户对问题的看法（用于相似度匹配）,
    mode:none

}

3.0 翻译用户回答：
information{
    mode:costom,
    user_answer:用户的回答


}

"""
# 存储多个角色的回答
answers=[]
# 从数据库中找角色在线生成
def process_news_data(informations_from_front):
        # 初始化回答列表
        global answers
        # 初始化
        answers=[]
        """
        处理问答数据的主要方法
        
        Args:
            informations_from_front:前端传递过来的新闻信息
            
            
        """
        mode =informations_from_front["mode"]
        topic=""
        news_title=""
        news_snippet=""
        question=""

        if mode=="news":
            print("新闻：\n")
            # 解析informations_from_front
            news_title = informations_from_front["title"]
            topic=informations_from_front["theme"]
            news_snippet = informations_from_front["snippet"]

            print("Title:", news_title)
            print("topic:", topic)
            print("Snippet:", news_snippet)
        else:
            print("新闻：\n")
            # 解析informations_from_front
            question = informations_from_front["question"]
            topic=informations_from_front["topic"]
            

            print("question:", question)
            print("topic:", topic)
            
        # 列出 Redis_db5 中的所有哈希键
        keys =redis_client_db5.keys('*')
        
      

        for key in keys:
            # 获取每个哈希键的 'topic' 字段
            topic_from_front = redis_client_db5.hget(key, 'topic')

            if topic_from_front:
                if isinstance(topic_from_front, bytes):
                    topic_from_front = topic_from_front.decode('utf-8')
                print(f"当前键 {key} 的 topic 是: {topic_from_front}")
               
                # 如果 'topic' 字段的值与传入的 topic_from_front 匹配
                if topic_from_front.strip() == topic.strip():
                    print("相等")
                    # 处理角色信息
                    role=redis_client_db5.hget(key,'role')
                    dialog=redis_client_db5.hget(key,'dialog')
                    
                    # (topic, role, question, dialog, mode,news_title=None,news_snippet=None
                    result=self.online_generate(
                       topic,role,question,dialog,mode,news_title,news_snippet
                    )    
                    
                    answers.append(result)
                    print(result,"\n");  
# answer,translation = online_generate(topic="仁", role="邝伟华", question="学习有什么用")
# print("answer:",answer)
# print("translation:",translation)

model= SentenceTransformer("model/embedding/m3e-base")
# 相似度匹配
def similarity_news_match(informations_from_front):
        """
            新闻相似度匹配
            answer_from_front:前端返回的回答
        """
        user_answer=informations_from_front["user_answer"]
        print(f"Received answer from front: {user_answer} ")
        library_answer_translations = []  # 用于存储答案的翻译
        library_answers = []  # 用于存储原始答案
        roles = []  # 存储对应的回答者
     
      
        # 在线生成
        print("Redis 中没有找到任何匹配的键。开始在线生成")
        process_news_data(informations_from_front=informations_from_front)
        for item in answers:
            library_answers.append(item["answer_part"])
            library_answer_translations.append(item["answer_translation"])
            roles.append(item["role"])

        # 对前端传来的回答进行编码
        embedding_front_answer = model.encode(user_answer)
        # 对筛选出的答案翻译进行编码
        embeddings_library_answer_translations = model.encode(library_answer_translations)
        
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
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Optional


# # 创建 FastAPI 实例
# app = FastAPI()


# # 定义请求的参数模型
# class GenerationRequest(BaseModel):
#     topic: str
#     role: str
#     question: str
#     dialog: Optional[str] = None # Optional 这个写法代表不是必须的参数
#     mode: Optional[str] = None  # 设置mode默认值为None


# # 定义生成回答的路由
# @app.post("/Lunyu_generate/")
# async def generate_answer(request: GenerationRequest):
#     try:
#         # 调用 online_generate 函数，获取回答和翻译
#         answer, translation = online_generate(
#             topic=request.topic,
#             role=request.role,
#             question=request.question,
#             dialog=request.dialog,
#             mode=request.mode,  # 使用请求中的mode（默认为None）
#         )
#         # 返回结果
#         return {"answer": answer, "translation": translation}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # 启动 FastAPI 服务
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=9090)
