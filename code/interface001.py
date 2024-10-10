# -*- coding: utf-8 -*-
"""
本文件包含对前端的两个接口：
1.0 获取前端的主题选择，后端从json文件或者数据库中匹配对应主题的问题，随机选中一个返回给前端
2.0 获取前端的回答，进行相似度匹配，将匹配结果返回给前端
3.0 25 行我使用了绝对路径，这里需要注意一下!!!!
"""

import json
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 一、 接口1
# 1.0 匹配主题
with open('D:\WorkSpace\VScodeProject\LunYuDemo\data\QA_with_topic.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


def match_theme(theme_from_front):
    # 读取JSON文件
    selected_question = ""
    # 将与theme_from_front相同的放到一个列表中
    questions = []
    for entry in data:

        # 提取主题和问题
        theme = entry['theme']
        print(theme)
        question = entry['question']

        if theme == theme_from_front:
            questions.append(question)
        # print(questions)

    # 去重
    questions = list(set(questions))
    print(questions)
    # 随机选出一个问题
    if questions:
        selected_question = random.choice(questions)
        print(selected_question)
        return selected_question
    else:
        print("没有匹配的问题。")


select_question = match_theme("孝道的理解")


# 接口1
@app.get("/get_question/")
def get_question(theme_from_front: str):
    question = match_theme(theme_from_front)

    if question:
        return {"question": question}
    else:
        # 没有找到匹配问题，返回404错误
        raise HTTPException(status_code=404, detail="没有匹配的问题。")


# 二、接口2
# 2.0 进行相似度匹配
"""
这里需要相似度匹配的结果函数，我暂时以similarity_match代替，
第二个接口的返回还要看函数的返回结果是一种什么形式，我暂时以result代替!!
"""


def similarity_match(answer_from_front):
    """
    这个函数内容来自 “群哥”
    :param str:
    :return:
    """
    return ""


@app.get("/get_answer/")
def get_question(answer_from_front: str):
    result = similarity_match(answer_from_front)

    if result:
        return {"question": result}
    else:
        # 没有找到匹配问题，返回404错误
        raise HTTPException(status_code=404, detail="没有匹配的问题。")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
