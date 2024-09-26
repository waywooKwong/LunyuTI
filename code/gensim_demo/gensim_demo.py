from gensim import corpora
from gensim.models import LdaModel
from pprint import pprint

# 创建文档集合
# documents = [
#     "Human machine interface for lab abc computer applications",
#     "A survey of user opinion of computer system response time",
#     "The EPS user interface management system",
#     "System and human system engineering testing of EPS",
#     "Relation of user perceived response time to error measurement",
#     "The generation of random binary unordered trees",
#     "The intersection graph of paths in trees",
#     "Graph minors IV Widths of trees and well quasi ordering",
#     "Graph minors A survey",
# ]
documents = ["子曰：“学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎",
             "子曰：“道千乘之国，敬事而信，节用而爱人，使民以时。",
             "子夏曰：“贤贤易色；事父母，能竭其力；事君，能致其身；与朋友交，言而有信。虽曰未学，吾必谓之学矣。"]

# 分词处理
texts = [[word for word in document.lower().split()] for document in documents]

# 创建词典
dictionary = corpora.Dictionary(texts)

# 创建文档-词频矩阵
corpus = [dictionary.doc2bow(text) for text in texts]

# 运行 LDA 模型
lda_model = LdaModel(corpus, num_topics=3, id2word=dictionary, passes=15)

# 打印主题
pprint(lda_model.print_topics())
