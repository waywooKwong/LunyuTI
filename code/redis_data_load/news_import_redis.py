import redis
import json

# 连接到 Redis 的 db
db_index = 6
r = redis.Redis(host='localhost', port=6379, db=db_index)

# 清空当前数据库
r.flushdb()
# 从 JSON 文件读取数据
with open('data/news_with_themes.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 将 JSON 数据导入 Redis
for idx, entry in enumerate(data):
    # 为每条新闻生成唯一键，例如 "news:<index>"
    key = f"news:{idx}"
    
    # 使用 hset 将每个字段存储为哈希
    r.hset(key, mapping={
        "title": entry["title"],
        "link": entry["link"],
        "snippet": entry["snippet"],
        "date": entry["date"],
        "source": entry["source"],
        "theme": entry["theme"],
        "img_url": entry["img_url"]
    })

print(f"数据已成功导入到 Redis db{db_index}。")
