"""
weihua 13/10/2024
1. 启动 redis
2. 检测本地 redis 各 db(0~15) 的情况, 
    在 db_index 设置为一个空的 db(最好统一设置为5, 不然后续接口函数还需要每次调整)
3. 直接运行该文件
    将数据导入到本地的数据库中
4. 检查数据库情况
"""
import redis
import json

# 连接到 Redis 的 db
db_index = 5
r = redis.Redis(host='localhost', port=6379, db=db_index)

# 从 JSON 文件读取数据
with open('code\\redis_data_load\\redis_db5_hash.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 将 JSON 中的 hash 数据导入 Redis
for key, hash_data in data.items():
    # 将每个 hash 键值对写入 Redis
    r.hmset(key, hash_data)

print(f"数据已成功导入到 Redis db{db_index}。")
