"""
20241013 - v1 
本代码是对应的 FastAPI 访问 Redis 数据库的接口
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

# 初始化 FastAPI 应用
app = FastAPI()

# 连接 Redis
r = redis.Redis(host="localhost", port=6379, db=0)


# 定义 Pydantic 模型，表示一个哈希条目
class ItemData(BaseModel):
    id: str
    topic: str
    question: str
    question_translation: str
    role: str
    role_dialog: str
    answer: str
    answer_translation: str


# 添加新的 Redis hash 数据 (hset + mapping)
@app.post("/item/add")
async def add_item(data: ItemData):
    r.hset(
        f"item:{data.id}",
        mapping={
            "topic": data.topic,
            "question": data.question,
            "question_translation": data.question_translation,
            "role": data.role,
            "role_dialog": data.role_dialog,
            "answer": data.answer,
            "answer_translation": data.answer_translation,
        },
    )
    return {"message": "Item added successfully"}


# 获取 hash 数据的接口 (hgetall)
@app.get("/item/get/{id}")
async def get_item(id: str):
    item_data = r.hgetall(f"item:{id}")
    if item_data:
        return {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in item_data.items()
        }
    else:
        raise HTTPException(status_code=404, detail="Item not found")


# 删除 hash 数据的接口 (删除整个 hash)
@app.delete("/item/delete/{id}")
async def delete_item(id: str):
    result = r.delete(f"item:{id}")
    if result:
        return {"message": "Item deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")
