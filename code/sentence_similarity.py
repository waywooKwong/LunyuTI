"""
20240923 - weihua
本代码是 all-MiniLM-L6-v2 是示例使用代码
根据语义相似度对句子进行相似度分数匹配

模型的 Huggingface 链接: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
"""

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("model\embedding\\all-MiniLM-L6-v2")
# sentence1 = "the topic is:'animal',the sentence is:'这是一只快乐的人'"
# sentence2 = "the topic is:'animal',the sentence is:'今天天气真好'"
sentence1 = "'这是一只快乐的人'"
sentence2 = "'今天天气真好'"

embeddings1 = model.encode(sentence1)
embeddings2 = model.encode(sentence2)

similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2)[0][0]
print("similarity_score:", similarity_score)
