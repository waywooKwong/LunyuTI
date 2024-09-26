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

# # 分角色加载内容
# ## 1.3 向量库加载
# # retriever链中预加载的文本

from document import Document
from langchain_community.vectorstores import Qdrant

docs_preload = []
prompt = """
    现在讨论的主题为：君子的憎恶，
    子贡对于这个话题曾发表的见解为：
    "恶徼以为知者，恶不孙以为勇者，恶讦以为直者。"
    """
role_overview = [
    "端木赐（公元前520年—公元前456年），复姓端木，字子贡。儒商鼻祖，春秋末年卫国黎（今河南省鹤壁市浚县）人。孔子的得意门生，儒家杰出代表，孔门十哲之一，善于雄辩，且有干济才，办事通达，曾任鲁国、卫国的丞相。还善于经商，是孔子弟子中的首富。“端木遗风”指子贡遗留下来的诚信经商的风气，成为民间信奉的财神。子贡善货殖，有“君子爱财，取之有道”之风，为后世商界所推崇。《论语》中对其言行记录较多，《史记》对其评价颇高。子贡死后，唐开元二十七年追封为“黎侯”，宋大中祥符二年加封为“黎公”，明嘉靖九年改称“先贤端木子”。"
]
docs_preload.append(
    Document(page_content=str(role_overview), metadata={"label": "role_overview"})
)

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
你目前的角色设定是：{prompt},\n

请用你的风格与我对话
"""

# 特定的输出格式字符串
input_str = """
{role_prompt}\n

这是我的问题：
{text_input}\n

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

import json

question = """
    当今时代出现了这样的社会事件：
        有些人以打假作为自己的职业，专门揭发制假卖假的企业
        
    请严格依据子贡发表过的见解，对上述事件做出评价
"""
print("processing now, question:", question)

# question 作为 text_input
prompt_str_input = prompt_template.format(text_input=question, role_prompt=role_prompt)
output_completion: AIMessage = retriever_chain.invoke(
    {"input": prompt_str_input, "chat_history": chat_history}
)
content = output_completion["answer"]
print("generating answer:", content)
