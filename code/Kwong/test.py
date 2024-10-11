import json

# 示例 JSON 字符串
json_str = """```json
{
    "answer": "夫子之行乎邦国，必闻其政事。然则求之与？抑与之与？曰：“吾闻之矣，无欲速而致远，无见小利而忘大谋。欲速则不达，见小利则大事不成。是以君子务本，本立而道生。治国之道在于正己以率下，修身以齐家，齐家以治国，此乃大道之行也。”"
}
```"""

# 去除开头和结尾的代码块标记
json_str = json_str.strip("```json\n").strip("```")
# print("json_str:", json_str)

# 解析 JSON 字符串
data = json.loads(json_str)

# 提取 answer 的内容
answer_content = data.get("answer", "")
# print("answer_content:", answer_content)

import redis

# 连接 Redis 数据库
# 默认 db=0, 这里使用 db=4, 避免与本地的 db 冲突
r = redis.StrictRedis(host="localhost", port=6379, db=4, decode_responses=True)


# 修改插入数据的函数，插入后确认数据
def insert_data_redis(topic, question, role, answer):
    # 使用 Redis 的 INCR 自增编号
    id = r.incr("entry_id")

    # 使用 hset 插入数据
    r.hset(
        f"item:{id}",
        mapping={
            "topic": topic,
            "question": question,
            "role": role,
            "answer": answer,
        },
    )
    print(f"Data inserted with ID: {id}")


# 插入数据示例
insert_data_redis("Topic 0", "Question 0", "Role 0", answer_content)
