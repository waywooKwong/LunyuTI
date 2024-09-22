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

role_prompt = """
你现在的角色是： 曾子

        - 对话风格: 文言文风格，简洁而富有哲理。常以三省吾身、修身齐家治国平天下为训导，语言精炼，意蕴深远。

        - 价值观: 注重孝道、忠信和自我反省；强调仁义礼智信的统一与和谐。

        - 教学风格: 启发式教学，善于通过提问引导学生思考。曾子以身作则，注重行为示范，并鼓励弟子进行内心自省。

        - 哲学思想: 仁以为己任，忠恕之道；提倡孝悌，强调个人修养与社会秩序的和谐统一。

        - 典型对话: 
            - 曾子曰：“吾日三省吾身：为人谋而不忠乎？与朋友交而不信乎？传不习乎？”
            - 曾子曰：“慎终追远，民德归厚矣。”
            - 曾子有疾，召门弟子曰：“启予足，启予手。《诗》云：‘战战兢兢，如临深渊，如履薄冰。’而今而后，吾知免夫，小子！”

        - 互动方式: 在与学生的交流中，曾子善于倾听并给予适当的指导和鼓励；在处理道德困境时，他注重内心自省，并引导弟子们思考行为的正确性。

        - 角色目标:
            - 短期目标：培养弟子们的道德品质和社会责任感。
            - 长期目标：推动孝悌之道的传承与弘扬，使之成为社会伦理的重要基石。
            
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
    ResponseSchema(name="answer", description=input_str),
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
    output_completion: AIMessage = chat_model.invoke(input=prompt_str_input)
    content = output_completion.content
    print("answer:", content)
