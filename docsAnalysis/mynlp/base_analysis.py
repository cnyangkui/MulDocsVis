# -*- encoding: utf-8 -*-
import os
import math
import pprint

from gensim import corpora, models, similarities, matutils
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


def similarity_by_group(corpus, ids, threshold=0.5):
    res = []
    length = len(ids)
    ids = [int(i) for i in ids]
    matrix = np.array(corpus['similarity'])
    for i in range(length-1):
        for j in range(i+1, length):
            value = matrix[ids[i]][ids[j]]
            if value > threshold:
                res.append({'source': ids[i], 'target': ids[j],
                            'similarity': round(float(value), 5)})
    return res

def extra_keywords_by_id(corpus, id=None, topK=5, ratio=0.05, withWeight=False):
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
    n = n_radio if n_radio > topK else topK
    words.sort(key=lambda d: d[1], reverse=True)
    words = words[:n]
    if withWeight:
        return list(map(lambda d: (corpus['dictionary'][d[0]], d[1]), words))
    else:
        return list(map(lambda d: corpus['dictionary'][d[0]], words))


def get_common_keywords(corpus, ids=list(), withWeight=5, ratio=0.05):
    """获取文档公共的关键词"""
    intersection = set()
    flag = True
    for id in ids:
        words = set(extra_keywords_by_id(corpus, int(id), withWeight=withWeight, ratio=ratio))
        if flag:
            intersection = words
            flag = False
        else:
            intersection = intersection & words
    return list(intersection)


def get_keywords_by_ids(corpus, ids=list(), topK=5):
    keywords = []
    for id in ids:
        words = extra_keywords_by_id(corpus, int(id), topK=topK, ratio=0)
        keywords.append({'id': id, 'words': words})
    return keywords


def get_common_words(corpus, ids=list()):
    """获取给定所有文档的公共词
    Args:
        ids: [id1, id2, ...]
    Returns:
        list, 公共词
    """
    intersection = set()
    flag = True
    for id in ids:
        bow = corpus['doc2bow'][int(id)]
        wordset = set(map(lambda d: d[0], bow))
        if flag:
            intersection = wordset
            flag = False
        else:
            intersection = intersection & wordset
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


def jieba_extra_keywords_from_bigdoc(sentences=list(), topK=20, withWeight=False):
    """将若干个文档合并成一个大文档，然后使用jieba抽取关键词"""
    bigdoc = ''
    for sentence in sentences:
        bigdoc += sentence
    return jieba_extra_keywords_from_doc(bigdoc, topK=topK, withWeight=withWeight)


def jieba_extra_keywords_from_docs(sentences=list(), topK=20):
    """使用jieba抽取多个文本的公共关键词"""
    common_keywords = set()
    flag = True
    for sentence in sentences:
        keywords = jieba.analyse.extract_tags(sentence, topK=topK, withWeight=False, allowPOS=(
            'n', 'nr', 'ns', 'nt', 'nw', 'nz', 'a', 'v', 'vn', 'x', 'PER', 'LOC', 'ORG'))
        keywords = set(keywords)
        if flag:
            common_keywords = keywords
            flag = False
        else:
            common_keywords = common_keywords & keywords
    return list(common_keywords)


def lda(corpus, num_topics=10, num_words=10):
    lda = models.LdaModel(corpus=corpus['doc2bow'], id2word=corpus['dictionary'], num_topics=num_topics)
    pprint.pprint(lda.print_topics(num_topics=num_topics, num_words=num_words))  # 把所有的主题打印出来看看


# lda(corpus, 100)
# print(similarity_by_id(corpus, 1))
# print(corpus['similarity'].similarity_by_id(1))

