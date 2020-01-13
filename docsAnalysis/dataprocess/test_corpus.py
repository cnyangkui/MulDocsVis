# -*- encoding: utf-8 -*-
import time
import pprint

from docsAnalysis import mynlp
from docsAnalysis.mynlp import utils

start = time.clock()

filedir = u'Y:/yk-file/文本数据/THUCNews/SmallTHUCNews'
# filedir = u'Y:/yk-file/文本数据/THUCNews/THUCNews/财经'
all_docs = utils.read_corpus(filedir)
pprint.pprint("读取文档结束...")
docs = all_docs[:10]

# 分词处理
corpus = mynlp.Corpus(docs)
corpus.tokenize()
pprint.pprint("分词结束...")

# 计算文档相似性矩阵
sm = corpus.get_similarity_matrix()
# pprint.pprint(sm)
utils.write_json(sm, '../output/sim_matrix.json')
pprint.pprint("计算相似性矩阵...")

# 文档投影
proj_data = corpus.proj_docs()
# pprint.pprint(proj_data)
utils.write_json(proj_data, '../output/proj.json')
pprint.pprint("投影结束...")

# 抽取关键词
all_keywords = corpus.extra_keywords(with_weight=False)
# pprint.pprint(all_keywords)
utils.write_json(all_keywords, '../output/keywords.json')
pprint.pprint("关键词抽取结束...")

# 聚类
labels = corpus.kmeans_docs(n_clusters=8)
print(labels)
utils.write_json(labels, '../output/cluster.json')
pprint.pprint("聚类结束...")

end = time.clock()
print("running time: ", end - start)
