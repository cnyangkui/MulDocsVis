# -*- encoding: utf-8 -*-
import csv
import pprint

from docsAnalysis.mynlp import mycorpus


def read_corpus(file_path):
    docs = []
    with open(file_path, 'r', encoding='gbk') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            docs.append(row['text'])
    return docs

file_path = '../crawler/nCovMemory.csv'
all_docs = read_corpus(file_path)
# all_docs = all_docs[:10]

# 分词处理
corpus = mycorpus.Corpus(all_docs)
corpus.set_tokenize_config(min_freq=2)
corpus.tokenize()
pprint.pprint("分词结束...")

# # 计算文档相似性矩阵
sm = corpus.cal_similarity_matrix()
# utils.write_json(sm, '../output/nCovMemory/similarity.json')
# corpus.save_similarity_index(u'../output/nCovMemory/similarity.index')
# pprint.pprint("计算相似性矩阵...")
#
# # 文档投影
# proj = corpus.proj_docs()
# projdata = []
# for index, doc in enumerate(all_docs):
#     projdata.append({'index': index, 'text': doc, 'x': proj[index][0], 'y': proj[index][1]})
# utils.write_json(projdata, '../output/nCovMemory/projdata.json', indent=4)
# utils.write_json(proj, '../output/nCovMemory/proj.json')
# pprint.pprint("投影结束...")
#
# # 抽取关键词
# all_keywords = corpus.extra_keywords(top_k=20, with_weight=False)
# utils.write_json(all_keywords, '../output/nCovMemory/keywords.json')
# pprint.pprint("关键词抽取结束...")
#
# # 聚类
# # labels = corpus.kmeans_docs(n_clusters=8)
# labels = corpus.kmeans_features(n_clusters=8, features=proj)
# utils.write_json(labels, '../output/nCovMemory/cluster.json')
# pprint.pprint("聚类结束...")
#
# # # 计算公共词比例
# # docpair2rate = corpus.common_word_rate()
# # utils.write_json(docpair2rate, '../output/nCovMemory/common_rate.json')

# LDA主题模型获取主题
# corpus.lda(10)

r_word_doc = corpus.word_doc_relation(rate_words=0.1)

def write_word_doc(desc, r_word_doc):
    fieldnames = {'Source', 'Target', 'Weight'}
    with open(desc, 'w', encoding='utf-8',  newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for d in r_word_doc:
            csv_writer.writerow({'Source': d['word'], 'Target': d['doc'], 'Weight': d['weight']})


def write_doc_sim(desc, matrix):
    fieldnames = {'Source', 'Target', 'Weight'}
    with open(desc, 'w', encoding='utf-8' ,newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for i in range(len(matrix) - 1):
            for j in range(i + 1, len(matrix)):
                csv_writer.writerow({'Source': i, 'Target': j, 'Weight': matrix[i][j]})


def write_merge(desc, r_word_doc, matrix):
    fieldnames = {'Source', 'Target', 'Weight'}
    with open(desc, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for d in r_word_doc:
            csv_writer.writerow({'Source': d['word'], 'Target': d['doc'], 'Weight': 1})
    with open(desc, 'a', encoding='utf-8' ,newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        # csv_writer.writeheader()
        for i in range(len(matrix) - 1):
            for j in range(i + 1, len(matrix)):
                csv_writer.writerow({'Source': i, 'Target': j, 'Weight': matrix[i][j]})

# write_doc_sim('../output/nCovMemory/r_sim.csv', sm)
# # write_word_doc('../output/nCovMemory/r_word_doc.csv', r_word_doc)
write_merge('../output/nCovMemory/r_rate0.1_weight1.csv', r_word_doc, sm)