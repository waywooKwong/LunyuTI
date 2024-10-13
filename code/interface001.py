# -*- coding: utf-8 -*-
"""
本文件包含对前端的两个接口：
1.0 获取前端的主题选择，后端从 json 文件或者数据库中匹配对应主题的问题，随机选中一个返回给前端
2.0 获取前端的回答，进行相似度匹配，将匹配结果返回给前端
"""

import json
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from sentence_transformers import SentenceTransformer, util

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前脚本所在目录
current_directory = os.path.dirname(os.path.abspath(__file__))

# 一、接口 1
# 1.0 匹配主题
data_file_path = os.path.join(current_directory, 'F:\learning\project\Lunyu\data\QA_with_topic.json')
with open(data_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)


def match_theme(theme_from_front):
    # 读取 JSON 文件
    selected_question = ""
    # 将与 theme_from_front 相同的放到一个列表中
    questions = []
    for entry in data:
        # 提取主题和问题
        theme = entry['theme']
        question = entry['question']
        if theme == theme_from_front:
            questions.append(question)

    # 去重
    questions = list(set(questions))

    # 随机选出一个问题
    if questions:
        selected_question = random.choice(questions)
        return selected_question
    else:
        print("没有匹配的问题。")
        return None


# 接口 1
@app.post("/get_question/")
def get_question(theme_from_front: str):
    question = match_theme(theme_from_front)
    if question:
        return {"question": question}
    else:
        # 没有找到匹配问题，返回 404 错误
        raise HTTPException(status_code=404, detail="没有匹配的问题。")


# 加载模型
model = SentenceTransformer("model/embedding/m3e-base")  

# 二、接口 2
# 2.0 进行相似度匹配

def similarity_match(answer_from_front):
    print(f"Received answer from front: {answer_from_front}")
    answers_file_path = os.path.join(current_directory, 'F:\learning\project\Lunyu\data\QA_with_topic.json')

    # 打开文件并读取内容
    with open(answers_file_path, 'r', encoding='utf-8') as answers_file:
        answer_library = json.load(answers_file)
        print(f"Answer library loaded successfully.")

    # 从库中提取所有的回答，用于计算相似度
    library_answers = [entry['answer'] for entry in answer_library]

    # 如果库里没有回答，直接返回 None
    if not library_answers:
        return None

    # 对前端传来的回答进行编码
    embedding_front_answer = model.encode(answer_from_front)

    # 对库中的回答进行编码
    embeddings_library_answers = model.encode(library_answers)

    # 计算前端回答与库中所有回答的余弦相似度
    cosine_similarities = util.pytorch_cos_sim(embedding_front_answer, embeddings_library_answers).flatten()

    # 打印出相似度列表，方便调试
    print(f"Cosine similarities: {cosine_similarities}")

    # 找出相似度最高的回答索引（随机打破平局）
    max_similarity = cosine_similarities.max().item()
    most_similar_indices = [i for i, similarity in enumerate(cosine_similarities) if similarity == max_similarity]
    most_similar_index = random.choice(most_similar_indices)  # 如果有多个相似度相同的答案，随机选择一个

    # 返回与相似度最高的回答对应的 entry
    most_similar_entry = answer_library[most_similar_index]

    # 输出相似回答
    most_similar_answer = most_similar_entry['answer']
    print(f"Most similar answer: {most_similar_answer}")

    return most_similar_answer


@app.get("/get_answer/")
def get_answer(answer_from_front: str):
    result = similarity_match(answer_from_front)
    if result:
        return {"answer": result}
    else:
        # 没有找到匹配问题，返回 404 错误
        raise HTTPException(status_code=404, detail="没有匹配的问题。")



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)