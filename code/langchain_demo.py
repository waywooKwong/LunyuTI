import datetime

# 标记时间戳，便于文件命名于标定时间
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. LangChain RAG 流程

## 1.1 设定选择模型，这里使用 ChatOllama
from langchain_community.chat_models import ChatOllama

model_name = "qwen2"  # llama3.1 / gemma2 / qwen2 ，可能中文的用qwen2 效果会好些？
chat_model = ChatOllama(model=model_name)

## 1.2 embeddings 模型（用 m3e-base），需要本地加载,，gitignore掉了
from langchain_huggingface import HuggingFaceEmbeddings

# 还没加载好
embeddings = HuggingFaceEmbeddings(
    model_name="model/m3e-base", model_kwargs={"device": "cuda"}
)
print("embedding info:", embeddings.model_name)

## 1.3 向量库加载
# retriever链中预加载的文本
from document import Document

docs_preload = []

# 添加文本的模板
docs_preload.append([Document(page_content="", metadata={"label": ""})])

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
        您现在是一个企业日常进行变更维护的工程师，\n
        你擅长通过读取记录变更服务相关指标判断变更是否导致发生异常并提供可能的修复措施。\n
        我现在有一些记录变更服务指标数据的领域文本文件信息，请判断这次变更是否符合预期。\n
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

fact_extraction_str = """
{text_input}
please strictly answer in format: 
{format_instruction}
"""

response_schema = [
    ResponseSchema(name="change_type", description=change_type_discription),
]

output_parser = StructuredOutputParser.from_response_schemas(
    response_schemas=response_schema
)

format_instruction = output_parser.get_format_instructions()
prompt_template = PromptTemplate.from_template(
    template=fact_extraction_str,
    partial_variables={"format_instruction": format_instruction},
)

prompt_str_input = prompt_template.format(
    text_input=target_doc, combine_classification=classification_response
)
output_completion: AIMessage = chat_model.invoke(input=prompt_str_input)
content = output_completion.content
