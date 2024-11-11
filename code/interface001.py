import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
import random
from Lunyu_generate_online import similarity_news_match,online_generate
import json
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接 Redis 数据库
redis_client = redis.Redis(host='localhost', port=6379, db=5)

# 加载模型
model = SentenceTransformer("model/embedding/m3e-base")

# 匹配主题并随机挑选问题
def match_theme(theme_from_front):
    # 列出 Redis 中的所有哈希键
    keys = redis_client.keys('*')
    print(f"Redis 中的所有键：{keys}")

    matched_questions = []

    for key in keys:
        # 获取每个哈希键的 'topic' 字段
        topic = redis_client.hget(key, 'topic')

        if topic:
            topic = topic.decode('utf-8')
            print(f"当前键 {key} 的 topic 是: {topic}")
            print(theme_from_front)
            # 如果 'topic' 字段的值与传入的 theme_from_front 匹配
            if topic == theme_from_front:
                # 获取该键下的 'question' 和 'question_translation' 字段
                question = redis_client.hget(key, 'question')
                question_translation = redis_client.hget(key, 'question_translation')

                if question and question_translation:
                    # 将问题和翻译加入匹配列表
                    matched_questions.append({
                        "question": question.decode('utf-8'),
                        "question_translation": question_translation.decode('utf-8')
                    })

    if matched_questions:
        # 随机返回一个匹配的问题
        return random.choice(matched_questions)

    print(f"没有找到与主题 {theme_from_front} 匹配的 topic。")
    return None
    

# 接口 1: 获取问题及其翻译
@app.get("/get_question/")
def get_question(theme_from_front: str):
    result = match_theme(theme_from_front)
    if result:
        return result
    else:
        # 没有找到匹配问题，返回 404 错误
        raise HTTPException(status_code=404, detail="没有找到匹配的问题。")

# 相似度匹配（根据 question_from_back 筛选，并通过 answer_translation 匹配，但返回 answer）
def similarity_match(question_from_back, answer_from_front):
    print(f"Received answer from front: {answer_from_front} and question: {question_from_back}")
    
    # 从 Redis 中获取所有哈希键
    keys = redis_client.keys('*')
    if not keys:
        print("Redis 中没有找到任何匹配的键。")
        return None

    library_answer_translations = []  # 用于存储答案的翻译
    library_answers = []  # 用于存储原始答案
    roles = []  # 存储对应的回答者
    key_mappings = []  # 存储键名，便于在相似度最高时查找

    for key in keys:
        question = redis_client.hget(key, 'question')
        answer = redis_client.hget(key, 'answer')
        answer_translation = redis_client.hget(key, 'answer_translation')
        role = redis_client.hget(key, 'role')
        
        if question and answer and answer_translation and role:
            question = question.decode('utf-8')
            if question == question_from_back:
                print("角色：",role.decode('utf-8'))
                print("回答：",answer.decode('utf-8'))

                library_answers.append(answer.decode('utf-8'))
                library_answer_translations.append(answer_translation.decode('utf-8'))
                roles.append(role.decode('utf-8'))
                key_mappings.append(key)

    if not library_answer_translations:
        print(f"没有找到与主题 {question_from_back} 匹配的答案翻译。")
        return None

    # 对前端传来的回答进行编码
    embedding_front_answer = model.encode(answer_from_front)
    # 对筛选出的答案翻译进行编码
    embeddings_library_answer_translations = model.encode(library_answer_translations)
    
    # 计算前端回答与库中所有筛选出的答案翻译的余弦相似度
    cosine_similarities = util.pytorch_cos_sim(embedding_front_answer, embeddings_library_answer_translations).flatten()
    print(f"Cosine similarities: {cosine_similarities}")
    
    # 找出相似度最高的答案索引（随机打破平局）
    max_similarity = cosine_similarities.max().item()
    most_similar_indices = [i for i, similarity in enumerate(cosine_similarities) if similarity == max_similarity]
    most_similar_index = random.choice(most_similar_indices)
    
    # 返回与相似度最高的原始答案和对应的角色
    most_similar_answer = library_answers[most_similar_index]
    corresponding_role = roles[most_similar_index]
    
    print(f"Most similar answer: {most_similar_answer}")
    print(f"Role: {corresponding_role}")
    
    return {
        "answer": most_similar_answer,
        "role": corresponding_role
    }

# 接口 2: 获取最相似的回答及其回答者（根据 question_from_back 筛选，并通过 answer_translation 匹配，但返回 answer））
@app.get("/get_answer/")
def get_answer(question_from_back: str, answer_from_front: str):
    result = similarity_match(question_from_back, answer_from_front)
    if result:
        return result
    else:
        # 没有找到匹配答案，返回 404 错误
        raise HTTPException(status_code=404, detail="没有找到匹配的答案。")


# 接口 3：返回新闻、自定义问题相似度匹配结果

# 3.1 展示新闻详情,获取前端点击的新闻（string）：待完善
"""
前端传递给后端的数据：
1.0 新闻：
information:{
    "title":新闻标题,
    "news_topic":新闻标题,
    "news_snippet"：新闻简介
    "user_answer":用户对新闻的看法（用于相似度匹配）,
    "mode":news

}
2.0 自定义问题

information:{
    topic:主题,
    question:自定义问题,
    user_answer:用户对问题的看法（用于相似度匹配）,
    mode:none

}

3.0 翻译用户回答：
information{
    mode:custom,
    user_answer:用户的回答


}

"""
@app.post("/online_generate/")
def get_answer(informations_from_front):
   
    decoded_informations_from_front = urllib.parse.unquote(informations_from_front)
    informations_from_front_dict = json.loads(decoded_informations_from_front)
    # 判断mode
    mode=informations_from_front_dict["mode"]
    # 如果是custom,直接将翻译结果返回前端
    if mode=="trans":
        print("翻译为古文")
        result=online_generate(role="论语风格古文翻译器",question=None,dialog=informations_from_front_dict["user_answer"],mode=mode,topic=None)
        answer_transwer_lunyu=result["answer_part"]
        return answer_transwer_lunyu
    else:

        print("json",decoded_informations_from_front)
        result =similarity_news_match(informations_from_front=informations_from_front_dict)
  
        if result:
            return result
        else:
            # 没有找到匹配答案，返回 404 错误
            raise HTTPException(status_code=404, detail="没有匹配到回答")

    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
