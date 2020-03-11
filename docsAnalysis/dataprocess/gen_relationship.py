import os
import csv
import math
import numpy as np

from docsAnalysis.mynlp import wr_tmp_data
from docsAnalysis.mynlp import base_analysis
from docsAnalysis.dataprocess import utils

corpus = wr_tmp_data.load_corpus_info()

def similarity(min_similarity=0.2):
    res = []
    size = len(corpus['doc2bow'])
    for i in range(size-1):
        tmp = base_analysis.similarity_by_id(corpus, i)
        for j in range(i+1, size):
            if tmp[j] > min_similarity:
                res.append({'Source': i, 'Target':j, 'Weight': tmp[j], 'type': 'doc'})
    return res


def doc2word():
    res = []
    size = len(corpus['doc2bow'])
    for i in range(size):
        keywords = base_analysis.extra_keywords_by_id(corpus, i, ratio=0.02)
        for word in keywords:
            res.append({'Source': i, 'Target': word, 'Weight': 1, 'type': 'word'})
    return res

res1 = similarity()
res2 = doc2word()
print(len(res1), len(res2))
res1.extend(res2)
print(len(res1))

utils.write_csv('../output/nCovMemory/r_doc2word.csv', res1)