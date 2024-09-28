import re
import json
import jieba
import gensim
from gensim import corpora
import pyLDAvis.gensim_models


# 分角色 JSON
json_path = "data\\role.json"
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# 将人物对话划分，以列表加载到 sentences 中
texts = []
for item in data:
    for content in item["contents"]:
        # content = re.sub('[\s+\. \!\/_,$% *(+\'""《》]+|[+--!,.?、~@#&%......&*():;‘]+',"",content["dialog"])
        dialog = re.sub(
            '[\s+\. \!\/_,$% *(+\'""“”《》]+|[+--!,.?、~@#&%......&*():;‘]+',
            "",
            content["dialog"],
        )
        texts.append(dialog)

# 定义停用词列表

## nltk 停词表
stopwords = set(["的", "了", "在", "是", "和", "不", "有", "乎"])  # 根据需要调整停用词

# 分词
texts = [[word for word in jieba.cut(text) if word not in stopwords] for text in texts]

# 创建字典和语料库
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

# 训练LDA模型
lda_model = gensim.models.LdaModel(corpus, num_topics=2, id2word=dictionary, passes=10)

import pyLDAvis.gensim_models

# 可视化
vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary)

# 保存为HTML文件
pyLDAvis.save_html(vis, "code\gensim_demo\lda_btml\lda_visualization.html")
