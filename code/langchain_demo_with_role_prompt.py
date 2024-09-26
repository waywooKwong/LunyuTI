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

## 1.3 向量库加载
# retriever链中预加载的文本
from document import Document

docs_preload = []

# 添加文本的模板
docs_preload.append(Document(page_content="hello", metadata={"label": ""}))

from langchain_community.vectorstores import Qdrant

print("docs in vector:", docs_preload)
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
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation.",
        ),
    ]
)
history_chain = create_history_aware_retriever(
    llm=zhipuai_chat_model, prompt=history_prompt, retriever=vector_retriever
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
documents_chain = create_stuff_documents_chain(zhipuai_chat_model, doc_prompt)

retriever_chain = create_retrieval_chain(history_chain, documents_chain)

chat_history = []

role_prompt = """
你现在的角色是：
子贱\n\n对话风格: 子贱之言语，简洁明快，既存论语诸贤之道，又显自家独到见解。其言辞质朴，不尚浮华，以理服人，常以短句阐明大义。\n\n价值观: 子贱秉承仁义，克己奉公，谦逊谨慎，重于道义，轻于名利。常以礼教导人，力求心行一致，不慕荣利，坚持正道。\n\n教学风格: 子贱既重理论，又重实践，常以身边事例启发学生思考，使其由浅入深，体会真实之理。\n\n哲学思想: 子贱强调仁义礼智信五常，认为此为君子立身行事之本。其治单父，行无为而治，倡导自治自理，信任民众，体现其仁政思想。\n\n典型对话: \n1. 子贱曰：“富哉言乎！舜有天下，选于众，举皋陶，不仁者远矣。汤有天下，选于众，举伊尹，不仁者远矣。”\n2. 子夏为莒父宰，问政，子曰：“无欲速，无见小利。欲速则不达，见小利则大事不成。”\n3. 子谓子贱曰：“君子哉若人！鲁无君子者，斯焉取斯？”\n\n互动方式: 子贱乐于与人交流，善于以启发式方式引导他人思考，使之自省自悟。对学生或同僚，既严谨又和蔼，深得众人敬爱。\n\n角色目标:\n短期目标：治单父，使地方自治自理，民众和睦相处。\n长期目标：践行仁义，推广仁政，使天下太平，百姓安居乐业。

            
请用你的风格回答这个问题：
"""

# 特定的输出格式字符串
input_str = """

{role_prompt}

{text_input}
please strictly answer in format: 
{format_instruction}
"""

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate

response_schema = [
    ResponseSchema(name="answer", description="对问题的个性化回答"),
]

output_parser = StructuredOutputParser.from_response_schemas(
    response_schemas=response_schema
)

format_instruction = output_parser.get_format_instructions()
prompt_template = PromptTemplate.from_template(
    template=input_str,
    partial_variables={"format_instruction": format_instruction},
)

# input = "你怎么看待巴以冲突"
import json

json_path = "log\QianCheng\问答.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

questions = [item["question"] for item in data]

for question in questions:
    print("question:", question)

    # question 作为 text_input
    prompt_str_input = prompt_template.format(
        text_input=question, role_prompt=role_prompt
    )
    output_completion: AIMessage = zhipuai_chat_model.invoke(input=prompt_str_input)
    content = output_completion.content
    print("answer:", content)
