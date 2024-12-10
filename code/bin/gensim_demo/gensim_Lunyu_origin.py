import re
import json
import gensim
from gensim.models import word2vec

# 分角色 JSON
json_path = "data\\role.json"
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# 将人物对话划分，以列表加载到 sentences 中
sentences = []
for item in data:
    role_name = item["name"]
    print("role name:", role_name)
    for content in item["contents"]:
        sentence = re.sub('[\s+\. \!\/_,$% *(+\'""《》]+|[+--!,.?、~@#&%......&*():;‘]+',"",content["dialog"])
        sentences.append(sentence)

# sentences = word2vec.LineSentence(sentences)
# model = word2vec.Word2Vec(sentences, hs=1,min_count=1,window=3,size=100)
# # 保存模型，以便重用
# model.save("model\gensim\Lunyu_test")
model = gensim.models.Word2Vec.load("model\gensim\Lunyu_test")

print(model.wv.index_to_key)  # 列出所有词汇

