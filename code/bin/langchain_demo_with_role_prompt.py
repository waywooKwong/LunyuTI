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
import os
import json
os.environ["ZHIPUAI_API_KEY"] = "0e863acacdc09cad69cd7865fc3e0a28.mhYC6Yl7joh1dCZ5"
    # 20240731 20:55 weihua
    # new key: "6ac43a47c3fed6a70433a55108033202.OMB8LBLcgcz60x3q"
    # old key: "43c5d0cda6ab08302d6db046469d7c6b.eCF9cwVy1tadDU1q"
    # qiancheng: "72fea15b5fce38e0a81b2bb01e4903dd.wkhUuC4oAO5otOmY"
from langchain_community.chat_models import ChatZhipuAI

zhipuai_chat_model = ChatZhipuAI(model="glm-4")
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
import json
all_prompt_json_path = "Lunyu\\all_prompts.json"
with open(all_prompt_json_path,'r',encoding='utf-8') as f:
    all_prompt = json.load(f)

from document import Document
from langchain_community.vectorstores import Qdrant

for item in all_prompt:
    role = item["name"]
    answer_file_path = f"data\\role_answer\{role}.txt"
    
    with open(answer_file_path,'a',encoding='utf-8') as file:
            file.write(f"role:{role}\n\n")
            
    print("processing now, role:",role)
    role_overview = item["overview"]
    prompt = item["prompt"]
    
    docs_preload = []

    # 添加文本的模板
    ## 这里加载 role_overview 用不用加切分工具？
    docs_preload.append(Document(page_content=str(role_overview), metadata={"label": "role_overview"}))
    
    # # 文档切分
    # from langchain.text_splitter import RecursiveCharacterTextSplitter
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=1)
    # chunked_documents = text_splitter.split_documents(documents=documents)

    # print("docs in vector:", docs_preload)
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
            "system","""
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

    json_path = "log\QianCheng\问答.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = [item["question"] for item in data]

    for question in questions:
        print("processing now, question:", question)

        # question 作为 text_input
        prompt_str_input = prompt_template.format(
            text_input=question, role_prompt=role_prompt
        )
        output_completion: AIMessage = retriever_chain.invoke(input=prompt_str_input)
        content = output_completion.content
        print("generating answer:", content)
        
        with open(answer_file_path,'a',encoding='utf-8') as file:
            file.write(f"question: {question}\n")
            file.write(f"answer: {content}\n")
            file.write("\n")
        
