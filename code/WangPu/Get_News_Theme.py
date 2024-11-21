# -*- coding: utf-8 -*-
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import WebBaseLoader
import os

import json
os.environ["ZHIPUAI_API_KEY"] = "0e863acacdc09cad69cd7865fc3e0a28.mhYC6Yl7joh1dCZ5"
    # 20240731 20:55 weihua
    # new key: "6ac43a47c3fed6a70433a55108033202.OMB8LBLcgcz60x3q"
    # old key: "43c5d0cda6ab08302d6db046469d7c6b.eCF9cwVy1tadDU1q"
    # qiancheng: "72fea15b5fce38e0a81b2bb01e4903dd.wkhUuC4oAO5otOmY"
from langchain_community.chat_models import ChatZhipuAI

zhipuai_chat_model = ChatZhipuAI(model="glm-4")
os.environ['USER_AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"

import json

# 假设 JSON 文件名为 "news_data.json"
file_path = "Lunyu\search_results.json"

# 打开并读取 JSON 文件
with open(file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)


# 问题主题
input=f"""
    分析以下主题\n
            
    从以下14个给定主题中选出来最符合该新闻的主题：\n
    贤者的品质\n
    孝道的理解\n
    美与艺术\n
    
    对生死的看法\n
    仁爱与智慧\n
    执政之道\n
    学习与志向\n
  
    君子的修养\n
    道德与礼仪\n
  

    教育与教导\n
    对友谊的看法\n

 
    道德修养\n
    以德治国\n
    社会和谐\n
    注意：只需选出主题即可，不需要多余的内容!!!!!!!!\n
    不超过7个字!!!\n
    只能选1个\n
    严格遵守以上规则


"""  
results = []
# 提取所有新闻条目的链接
for news_item in json_data["news"]:
    title=news_item["title"]
    link=news_item["link"]
    snippet=news_item["snippet"]
    date=news_item["date"]
    source=news_item["source"]
    img_url=news_item["imageUrl"]



    print(news_item["link"])
    # 2-2. 加载网页
    loader = WebBaseLoader(
        web_path=news_item["link"]
    )

    docs = loader.load()
    print(docs)

    # 生成分词和切分器
    text_splitter = RecursiveCharacterTextSplitter()
    from langchain_huggingface import HuggingFaceEmbeddings

    # 对文档进行分词和切分
    documents = text_splitter.split_documents(documents=docs)
    print(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="model\embedding\m3e-base", model_kwargs={"device": "cpu"}
    )
    print("embedding loading:", embeddings.model_name)
    from document import Document
    from langchain_community.vectorstores import Qdrant
    vectorstore = Qdrant.from_documents(
        documents=documents,
        embedding=embeddings,
        location=":memory:",
        collection_name="my_documents"
    )
    from langchain.chains import create_history_aware_retriever
    from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

    # Generate LLM chat model
    chat_model =zhipuai_chat_model
    retriever = vectorstore.as_retriever()
    # Generate ChatModel session prompt messages
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user",
        "Given the above conversation, generate a search query to look up in order to get information relevant to the "
        "conversation.")
    ])
    retriever_chain = create_history_aware_retriever(chat_model, retriever, prompt)
    # Continue retrieval, remember retrieved documents, etc.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Please prioritize the provided document information when answering the user's questions:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain

    documents_chain = create_stuff_documents_chain(chat_model, prompt)
    #最终的retriever_chain
    chat_history = []

    retriever_chain = create_retrieval_chain(retriever_chain, documents_chain)

    print("***************************************************************************************\n")

    topic=retriever_chain.invoke({
            "input":input,
            "chat_history": chat_history,
        })
    
    print(topic["answer"])
    news_result = {
        "title": title,
        "link": link,
        "snippet": snippet,
        "date": date,
        "source": source,
        "theme": topic["answer"],
        "img_url":img_url
    }
    results.append(news_result)


    print("***************************************************************************************\n")

# 最后将结果保存到一个新的JSON文件
output_file = "Lunyu/news_with_themes01.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"所有结果已保存到 {output_file}")