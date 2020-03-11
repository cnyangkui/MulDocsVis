# -*- encoding: utf-8 -*-
import os
import math
import pprint
from functools import reduce

from gensim import corpora, models, similarities, matutils
from gensim.test.utils import get_tmpfile
import numpy as np
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

from docsAnalysis.mynlp import wr_tmp_data

corpus = wr_tmp_data.load_corpus_info()


def proj_docs(corpus, n_components=2):
    """文档投影"""
    features = matutils.corpus2dense(corpus['tfidfcorpus'], num_terms=len(corpus['dictionary'].keys()),
                                     num_docs=len(corpus['doc2bow'])).T
    proj_data = TSNE(n_components=n_components, random_state=0).fit_transform(features)
    proj_data = np.array(proj_data, dtype='float')
    return proj_data.tolist()


def kmeans_docs(corpus, n_clusters=8):
    """文档聚类"""
    features = matutils.corpus2dense(corpus['tfidfcorpus'], num_terms=len(corpus['dictionary'].keys()),
                                     num_docs=len(corpus['doc2bow'])).T
    db = KMeans(n_clusters=n_clusters, random_state=0).fit(features)
    return db.labels_.tolist()


def kmeans_features(self, n_clusters=8, features=None):
    """特征聚类"""
    db = KMeans(n_clusters=n_clusters, random_state=0).fit(features)
    return db.labels_.tolist()


def extra_all_keywords(corpus, top_k=10, with_weight=False):
    """抽取关键词"""
    all_keywords = []
    for doc in corpus['tfidfcorpus']:
        sorted_doc = sorted(doc, key=lambda d: d[1], reverse=True)
        if with_weight:
            keywords = [(corpus['dictionary'][d[0]], d[1]) for d in sorted_doc[:top_k]]
        else:
            keywords = [corpus['dictionary'][d[0]] for d in sorted_doc[:top_k]]
        all_keywords.append(keywords)
    return all_keywords


def similarity_by_id(corpus, id):
    """获取一个文档与其它所有文档的相似度"""
    res = corpus['similarity'].similarity_by_id(id)
    res = np.array(res, dtype='float')
    res = np.around(res, 5)
    return res.tolist()

def similarity_by_ids(corpus, id1, id2):
    """获取两个文档间的相似度"""
    res = similarity_by_id(corpus, id1)
    return res[id2]

def extra_keywords_by_id(corpus, id=None, n_min=5, ratio=0.05, with_weight=False):
    """
    抽取文档id为docid的关键词，关键词按权重降序排列
    Args:
        corpus: 语料库信息，包括词典，词袋模型，tfidf模型，相似性矩阵
        docid: 文档id
        n_min: 最少关键词数量
        ratio：按文档词语数量比例抽取关键词
        with_weight: 抽取的关键词是否返回tf-idf权重
    Returns:
        不带权重：[word1, word2, ... ]
        带权重：[(word, weight), ...]
    """
    if id is None:
        return None
    words = corpus['tfidfcorpus'][id]
    n_radio = math.floor(len(words) * ratio)
    n = n_radio if n_radio > n_min else n_min
    words.sort(key=lambda d: d[1], reverse=True)
    words = words[:n + 1]
    if with_weight:
        return list(map(lambda d: (corpus['dictionary'][d[0]], d[1]), words))
    else:
        return list(map(lambda d: corpus['dictionary'][d[0]], words))


def get_common_keywords(corpus, id1, id2):
    """获取两个文档公共的关键词"""
    words1 = set(extra_keywords_by_id(corpus, id1))
    words2 = set(extra_keywords_by_id(corpus, id2))
    intersection = words1 & words2
    return list(intersection) if len(intersection) > 0 else None


def get_common_words(corpus, id1, id2):
    """获取两个文档的公共词
    Args:
        id1: 第一篇文档的id
        id2：第二篇文档的id
    Returns:
        {commonwords: list, ratio: float}
        commonwords为公共词，ratio为公共词占所有词的比例
    """
    docbow1 = corpus['doc2bow'][id1]
    docbow2 = corpus['doc2bow'][id2]
    words1 = set(map(lambda d: d[0], docbow1))
    words2 = set(map(lambda d: d[0], docbow2))
    intersection = words1 & words2
    union = words1 | words2
    return {
        'commonwords': [corpus['dictionary'][index] for index in intersection],
        'ratio': len(intersection) / len(union)
    }


a = get_common_words(corpus, 103, 100)
pprint.pprint(a)
