import json
import os

os.environ["ZHIPUAI_API_KEY"] = "0e863acacdc09cad69cd7865fc3e0a28.mhYC6Yl7joh1dCZ5"
    # 20240731 20:55 weihua
    # new key: "6ac43a47c3fed6a70433a55108033202.OMB8LBLcgcz60x3q"
    # old key: "43c5d0cda6ab08302d6db046469d7c6b.eCF9cwVy1tadDU1q"
    # qiancheng: "72fea15b5fce38e0a81b2bb01e4903dd.wkhUuC4oAO5otOmY"
from langchain_community.chat_models import ChatZhipuAI

zhipuai_chat_model = ChatZhipuAI(model="glm-4")
# -*- coding: utf-8 -*-
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncIterable, List
dialog="00000"
name="子贡"
theme=""

# json_path = "D:\WorkSpace\VScodeProject\LunYuDemo\log\WangPu\论语全角色对话.json"  # 使用原始字符串

# json_path = "D:\WorkSpace\VScodeProject\LunYuDemo\log\WangPu\论语全角色对话.json"  # 使用原始字符串
json_path = "log\QianCheng\问答.json"  # 或使用双反斜杠
data_dicts = []  # 用于存储所有的字典
sentences=[]
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)


sum=0
for entry in data:
    topic=entry["topic"]
    question = entry["question"]
    answer=entry["answer"]
    source=entry["source"]
    translation=entry["translation"]  
    # 问题主题
    prompt=f"""
            分析以下主题\n
            {topic}\n
            从以下20个给定主题中选出来最符合该句子的主题：\n
            贤者的品质\n
            孝道的理解\n
            美与艺术\n
            为人处世的原则\n
            对生死的看法\n
            仁爱与智慧\n
            执政之道\n
            学习与志向\n
            人际关系\n
            君子的修养\n
            道德与礼仪\n
            责任与担当\n
            自我反省\n
            教育与教导\n
            对友谊的看法\n
            权力与责任\n
            信任与信用\n
            道德修养\n
            以德治国\n
            社会和谐\n
            注意：只需选出主题即可，不需要多余的内容!!!!!!!!\n
            不超过7个字!!!\n
            只能选1个\n
            严格遵守以上规则


    """  
    theme=zhipuai_chat_model.invoke(prompt).content
    data_dict = {
        "theme": theme,
        "question" : question,
        "answer":answer,
        "source":source,
        "translation":translation
    }
    # 将数据字典添加到列表中
    data_dicts.append(data_dict)
    print(data_dict["theme"])
    print(data_dict["question"])

    
    print("=================================================================")


    


# 将所有字典保存到 JSON 文件中
output_file = 'code\WangPu\问题主题归类结果.json'  # 你想要保存的文件名
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data_dicts, f, ensure_ascii=False, indent=4)

print(f"数据已成功保存到 {output_file}。")