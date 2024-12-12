# -*- coding: utf-8 -*-
"""

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

user_prompt = "使用类图，描述一个学院的管理架构图"
mermaid_role = """
Summary of UML Diagrams Supported by Mermaid:

    - Class Diagram: Shows classes, attributes, methods, and relationships (inheritance, aggregation).
    - Sequence Diagram: Shows interactions between objects in a sequence of events.
    - Use Case Diagram: Represents actors and their use cases within a system.
    - State Diagram: Models the states and transitions of an object.
    - Activity Diagram: Models the flow of control or data in a process.
    - Component Diagram: Describes the relationships and dependencies between components in a system.
    - Deployment Diagram: Represents the physical deployment of components onto hardware nodes.

When about relationship between different object, Following rules below:

    - "--" Indicates a common association. 
    - "o--" stands for Aggregation. 
    - "*--" Indicates Composition. 
    - "1--" Indicates a one-to-one relationship.
"""

# 标记时间戳，便于文件命名于标定时间
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

import redis

# 连接 Redis 数据库
# 默认 db=0, 这里使用 db=4, 避免与本地的 db 冲突
r = redis.StrictRedis(host="localhost", port=6379, db=4, decode_responses=True)

# 1. LangChain RAG 流程

## 1.1 设定选择模型，这里使用 ChatOllama
from langchain_community.chat_models import ChatOllama

model_name = "qwen2.5-coder"
chat_model = ChatOllama(model=model_name)

## 1.2 embeddings 模型（用 m3e-base），需要本地加载,，gitignore掉了
from langchain_huggingface import HuggingFaceEmbeddings

# 这里先确认模型有没有加载到本地
embeddings = HuggingFaceEmbeddings(
    model_name="model\embedding\m3e-base", model_kwargs={"device": "cpu"}
)
print("embedding loading:", embeddings.model_name)

## 1.3 向量库加载
# retriever链中预加载的文本

from document import Document
from langchain_community.vectorstores import Qdrant
import json
import re

docs_preload = []

docs_preload.append(
    Document(
        page_content=str(),
        metadata={"label": "role_overview"},
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

history_prompt: ChatPromptTemplate = (
    ChatPromptTemplate.from_messages(
        messages=[
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", """需求的描述是{input}"""),
            (
                "user",
                "Given the introduction in docs, generate answer in corresponding view",
            ),
        ]
    )
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
        Act as a professional UML generation tool. 
        Generate accurate Mermaid code to represent my requirements as a UML diagram.
        {context}
        """,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ]
)
documents_chain = create_stuff_documents_chain(
    chat_model, doc_prompt
)
retriever_chain = create_retrieval_chain(
    history_chain, documents_chain
)

chat_history = []
role_prompt = f"""
Act as a professional UML generation tool. 
Generate accurate Mermaid code to represent my requirements as a UML diagram.
This is the task: 
{user_prompt}

This is mermaid role: 
{mermaid_role}
Place answer in English.
"""
print("role_prompt:", role_prompt)

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
        name="Mermaid_code",
        description="Mermaid code corresponding to UML diagram",
    ),
]

output_parser = StructuredOutputParser.from_response_schemas(
    response_schemas=response_schema
)

format_instruction = output_parser.get_format_instructions()
prompt_template = PromptTemplate.from_template(
    template=input_str,
    partial_variables={
        "format_instruction": format_instruction
    },
)

prompt_str_input = prompt_template.format(
    role_prompt=role_prompt
)
output_completion: AIMessage = retriever_chain.invoke(
    {"input": prompt_str_input, "chat_history": chat_history}
)
content = output_completion["answer"]
print("Mermaid_code:", content)

# # print("generating answer:", content)

# # 去除开头和结尾的代码块标记
# json_str = content.strip("```json\n").strip("```")
# # print("json_str:", json_str)

# # 删除 {""}
# content_processed = re.sub(
#     r'[{}"“” ]+', "", json_str
# )  # 删除 '{' 和 '"' 符号
# # print("cleaned_data:", content_processed)

# # 提取 Mermaid_code: 后的内容
# start_index_translation = content_processed.find(
#     "Mermaid_code:"
# ) + len("Mermaid_code:")
# answer_translation = content_processed[
#     start_index_translation:
# ].strip()  # 去掉前后空格

# print("Mermaid_code:", answer_translation)

print("==== ====\n")
