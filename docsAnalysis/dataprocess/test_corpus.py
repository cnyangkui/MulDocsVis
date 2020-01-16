# -*- encoding: utf-8 -*-
import time
import pprint

from docsAnalysis import mynlp
from docsAnalysis.mynlp import utils

start = time.clock()

# filedir = u'Y:/yk-file/文本数据/THUCNews/SmallTHUCNews'
# filedir = u'Y:/yk-file/文本数据/THUCNews/THUCNews/财经'
filedir = u'Y:/yk-file/文本数据/THUCNews/财经5000'
all_docs = utils.read_corpus(filedir)
pprint.pprint("读取文档结束...")

# 分词处理
corpus = mynlp.Corpus(all_docs)
corpus.tokenize()
pprint.pprint("分词结束...")

# 计算文档相似性矩阵
sm = corpus.cal_similarity_matrix()
# utils.write_json(sm, '../tmp/sim_matrix.json')
corpus.save_similarity_index(u'../output/similarity.index')
pprint.pprint("计算相似性矩阵...")


# 文档投影
proj_data = corpus.proj_docs()
utils.write_json(proj_data, '../output/proj.json')
pprint.pprint("投影结束...")

# 抽取关键词
all_keywords = corpus.extra_keywords(with_weight=False)
utils.write_json(all_keywords, '../output/keywords.json')
pprint.pprint("关键词抽取结束...")

# 聚类
labels = corpus.kmeans_docs(n_clusters=8)
utils.write_json(labels, '../output/cluster.json')
pprint.pprint("聚类结束...")

end = time.clock()
print("running time: ", end - start)
