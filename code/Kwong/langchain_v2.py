# -*- coding: utf-8 -*-
"""
22/09/2024 - v1 - weihua
这是 langchain 获得每个角色对全部问题回答的链
目前链子的流程已经基本跑通，实现了从 log\QianCheng\问答.json 读取问题并回答

还欠缺：
1. 角色信息加入 prompt
2. 输出的格式处理/加入数据库

23/09/2024 - v2 - weihua
这版在 input_str 中加入了一个 role_prompt 参数作为测试使用

23/09/2024 - v3 - weihua
接入 role prompt 令每一个角色对问题进行回答

02/10/2024 - weihua
根据 QA_with_topic.json 每个问题
匹配 topic.json 中的每条目角色回答
生成对对应问题的回答
"""

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
import datetime

# 标记时间戳，便于文件命名于标定时间
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. LangChain RAG 流程

## 1.1 设定选择模型，这里使用 ChatOllama
from langchain_community.chat_models import ChatOllama

model_name = "Lunyu"  # 这里的 Lunyu 模型是 Ollama 基于 Qwen2.5 生成的
chat_model = ChatOllama(model=model_name)

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

"""
QA_with_topic.json 每条目加载
每一条目："theme", "question", "answer", "source", "translation"
"""
json_path = "data\QA_with_topic.json"
with open(json_path, "r", encoding="utf-8") as file:
    topic_based_data = json.load(file)

for item in topic_based_data:
    topic = item["theme"]
    print("\ntopic:", topic)
    question = item["question"]
    print("question:", question)

    topic_json_path = "data\\topic.json"
    with open(topic_json_path, "r", encoding="utf-8") as file:
        topic_data = json.load(file)
    
    # 从 topic.json 中提取对应主题的文本
    for item in topic_data:
        if item["class"] == topic:
            contents = item["contents"]
            for content in contents:
                # 人物名称
                role = content["name"]
                # 人物对该主题发表过的见解
                dialog = content["dialog"]
                prompt = f"""
                现在讨论的主题为：{topic},
                有人提出这样一个问题：{question},
                论语中人物：{role},
                曾经对这个话题发表过见解：{dialog}
                """

                # 加载人物相关描述的数据
                role_json_path = "data\\role.json"
                with open(role_json_path, "r", encoding="utf-8") as file:
                    role_data = json.load(file)

                for role_item in role_data:
                    if role_item["name"] == role:
                        role_overview = role_item["story"]
                        role_comments = role_item["comments"]
                        docs_preload = []
                
                        docs_preload.append(Document(page_content=str(role_overview), metadata={"label": "role_overview"}))
                        docs_preload.append(Document(page_content=str(role_comments), metadata={"label": "role_comments"}))
                        
                        # 向量库加载角色信息的描述
                        vector = Qdrant.from_documents(
                        documents=docs_preload,
                        embedding=embeddings,
                        location=":memory:",
                        collection_name="preload_docs",)
                        
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
                            llm=chat_model, prompt=history_prompt, retriever=vector_retriever
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
                        role_prompt = f"""
                        你目前的角色设定是：
                        {prompt}, 
                        请用你的风格与我对话，发表你对问题的见解
                        """
                        print("role_prompt:",role_prompt)

                        # 特定的输出格式字符串
                        input_str = """
                        {role_prompt}\n

                        please strictly answer in format: 
                        {format_instruction}
                        """

                        from langchain.output_parsers import ResponseSchema, StructuredOutputParser
                        from langchain_core.prompts import PromptTemplate

                        response_schema = [
                            ResponseSchema(name="answer", description="用论语的文言文文风回答"),
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
                        print("generating answer:", content)
                        
                        file_path = f"data\\role_answer\{timestamp}_answer.txt"
                        with open(file_path,'+a',encoding='utf-8') as file:
                            file.write(f"role_prompt:{role_prompt}")
                            file.write(f"generating answer:{content}\n\n")
                            
                        print("==== ====\n")
        # else:
        #     print("Not find content concerning topic")