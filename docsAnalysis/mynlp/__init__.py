# -*- encoding: utf-8 -*-
import os
from collections import defaultdict
import re
import pprint
import jieba
import jieba.posseg
import jieba.analyse
from gensim import corpora, models, similarities, matutils
from gensim.test.utils import get_tmpfile
import numpy as np
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))


class Corpus(object):

    def __init__(self, corpus):
        self.corpus = corpus
        self.stopwords = list()
        self.tokenize_config = {
            'min_freq': 1,
            'with_pos': ['n', 'nr', 'ns', 'nt', 'nw', 'nz', 'v', 'a', 'PER', 'LOC', 'ORG']
        }
        self.__dictionary = None
        self.__bow_corpus = None
        self.__tfidf_corpus = None
        self.__tfidf_model = None

        self.set_stop_words(_get_abs_path(u'哈工大停用词表.txt'))

    def set_stop_words(self, file_path):
        """从停用词表获取停用词"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                self.stopwords.append(line.strip())
        return self.stopwords

    def set_tokenize_config(self, min_freq=1):
        """分词处理设置"""
        self.tokenize_config['min_freq'] = min_freq

    def tokenize(self):
        """分词，去停用词，构建向量空间模型"""
        docs = []
        frequency = defaultdict(int)
        for text in self.corpus:
            text = re.sub(r'[a-zA-Z0-9]', ' ', text)
            text = re.sub(r'\s', '', text)
            word_pos = jieba.posseg.cut(text)
            words = [word for word, flag in word_pos if
                     len(word) > 1 and word not in self.stopwords and flag in self.tokenize_config['with_pos']]
            for word in words:
                frequency[word] += 1
            docs.append(words)
        docs = [[word for word in doc if frequency[word] > self.tokenize_config['min_freq']] for doc in docs]
        self.__dictionary = corpora.Dictionary(docs)
        print(self.__dictionary)
        self.__bow_corpus = [self.__dictionary.doc2bow(doc) for doc in docs]
        self.__tfidf_model = models.TfidfModel(self.__bow_corpus)
        self.__tfidf_corpus = self.__tfidf_model[self.__bow_corpus]

    def get_similarity_matrix(self):
        """计算文档相似性矩阵"""
        index_temp = get_tmpfile("index")
        index = similarities.Similarity(index_temp, self.__tfidf_corpus, num_features=len(self.__dictionary))
        # index = similarities.MatrixSimilarity(self.__tfidf_corpus)
        sim_matrix = np.array(index, dtype='float')
        return np.around(sim_matrix, 5).tolist()

    def proj_docs(self, n_components=2):
        """文档投影"""
        features = matutils.corpus2dense(self.__tfidf_corpus, num_terms=len(self.__dictionary),
                                         num_docs=len(self.corpus)).T
        proj_data = TSNE(n_components=n_components, random_state=0).fit_transform(features)
        proj_data = proj_data.astype(np.float)
        return np.around(proj_data, 5).tolist()

    def kmeans_docs(self, n_clusters=8):
        """文档聚类"""
        features = matutils.corpus2dense(self.__tfidf_corpus, num_terms=len(self.__dictionary.keys()),
                                         num_docs=len(self.corpus)).T
        db = KMeans(n_clusters=n_clusters, random_state=0).fit(features)
        return db.labels_.tolist()

    def extra_keywords(self, top_k=10, with_weight=False):
        """抽取关键词"""
        all_keywords = []
        for doc in self.__tfidf_corpus:
            sorted_doc = sorted(doc, key=lambda d: d[1], reverse=True)
            if with_weight:
                keywords = [(self.__dictionary[d[0]], d[1]) for d in sorted_doc[:top_k]]
            else:
                keywords = [self.__dictionary[d[0]] for d in sorted_doc[:top_k]]
            all_keywords.append(keywords)
        return all_keywords
