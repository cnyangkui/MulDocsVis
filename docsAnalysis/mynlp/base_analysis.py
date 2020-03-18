# -*- encoding: utf-8 -*-
import os
import math
import pprint
from functools import reduce

from gensim import corpora, models, similarities, matutils
from gensim.test.utils import get_tmpfile
import numpy as np
import jieba
import jieba.analyse
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

from docsAnalysis.mynlp import wr_tmp_data

corpus = wr_tmp_data.load_corpus_base_info()

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))

jieba.load_userdict(_get_abs_path('dict.txt'))
print("load dict.txt...")
jieba.analyse.set_stop_words(_get_abs_path('哈工大停用词表.txt'))
print("load 哈工大停用词表...")


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
    words = corpus['tfidfcorpus'][int(id)]
    n_radio = math.floor(len(words) * ratio)
    n = n_radio if n_radio > n_min else n_min
    words.sort(key=lambda d: d[1], reverse=True)
    words = words[:n + 1]
    if with_weight:
        return list(map(lambda d: (corpus['dictionary'][d[0]], d[1]), words))
    else:
        return list(map(lambda d: corpus['dictionary'][d[0]], words))


def get_common_keywords(corpus, ids=list(), n_min=5, ratio=0.05):
    """获取文档公共的关键词"""
    intersection = set()
    for id in ids:
        words = set(extra_keywords_by_id(corpus, int(id), n_min=n_min, ratio=ratio))
        if intersection:
            intersection = intersection & words
        else:
            intersection = words
    return list(intersection)


def get_common_words(corpus, ids=list()):
    """获取给定所有文档的公共词
    Args:
        ids: [id1, id2, ...]
    Returns:
        list, 公共词
    """
    intersection = set()
    count = 0
    for id in ids:
        bow = corpus['doc2bow'][int(id)]
        wordset = set(map(lambda d: d[0], bow))
        if count == 0:
            intersection = wordset
        else:
            intersection = intersection & wordset
        count += 1
    return [corpus['dictionary'][wordindex] for wordindex in intersection]


def build_tfidf_vsm(corpus):
    features = matutils.corpus2dense(corpus['tfidfcorpus'], num_terms=len(corpus['dictionary'].keys()),
                                     num_docs=len(corpus['doc2bow'])).T
    return features


def jieba_extra_keywords_from_doc(sentence='', topK=20, withWeight=False):
    """使用jieba抽取一个文本的关键词"""
    keywords = jieba.analyse.extract_tags(sentence, topK=topK, withWeight=withWeight, allowPOS=(
        'n', 'nr', 'ns', 'nt', 'nw', 'nz', 'a', 'v', 'vn', 'x', 'PER', 'LOC', 'ORG'))
    return keywords


def jieba_extra_keywords_from_docs(sentences=list(), topK=20):
    """使用jieba抽取多个文本的公共关键词"""
    common_keywords = set()
    count = 0
    for sentence in sentences:
        keywords = jieba.analyse.extract_tags(sentence, topK=topK, withWeight=False, allowPOS=(
            'n', 'nr', 'ns', 'nt', 'nw', 'nz', 'a', 'v', 'vn', 'x', 'PER', 'LOC', 'ORG'))
        keywords = set(keywords)
        if count == 0:
            common_keywords = keywords
        else:
            common_keywords = common_keywords & keywords
        count += 1
    return list(common_keywords)


def lda(corpus, num_topics=10, num_words=20):
    lda = models.LdaModel(corpus=corpus['doc2bow'], id2word=corpus['dictionary'], num_topics=num_topics)
    pprint.pprint(lda.print_topics(num_topics=num_topics, num_words=num_words))  # 把所有的主题打印出来看看


# corpus = wr_tmp_data.load_corpus_base_info()
# lda(corpus, 100, 100)
# get_common_words(corpus, [1, 2, 3])
