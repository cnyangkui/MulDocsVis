# -*- encoding: utf-8 -*-
import os
import math
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
        self.tokenized_docs = list()
        self.stopwords = list()
        self.tokenize_config = {
            'min_freq': 5,
            'with_pos': ['n', 'nr', 'ns', 'nt', 'nw', 'nz', 'a', 'v', 'vn', 'x', 'PER', 'LOC', 'ORG']
        }
        self.__dictionary = None
        self.__bow_corpus = None
        self.__tfidf_corpus = None
        self.__tfidf_model = None
        self.__similarity_index = None

        self.set_stop_words(_get_abs_path(u'哈工大停用词表.txt'))
        jieba.load_userdict(_get_abs_path('dict.txt'))

    @property
    def dictionary(self):
        return self.__dictionary

    @property
    def bow_corpus(self):
        return self.__bow_corpus

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
        self.tokenized_docs = [[word for word in doc if frequency[word] > self.tokenize_config['min_freq']] for doc in docs]
        self.__dictionary = corpora.Dictionary(self.tokenized_docs)
        self.__bow_corpus = [self.__dictionary.doc2bow(doc) for doc in self.tokenized_docs]
        self.__tfidf_model = models.TfidfModel(self.__bow_corpus)
        self.__tfidf_corpus = self.__tfidf_model[self.__bow_corpus]

    def cal_similarity_matrix(self):
        """计算文档相似性矩阵"""
        index_temp = get_tmpfile("index")
        self.__similarity_index = similarities.Similarity(index_temp, self.__tfidf_corpus, num_features=len(self.__dictionary))
        # index = similarities.MatrixSimilarity(self.__tfidf_corpus)
        sim_matrix = np.array(self.__similarity_index, dtype='float')
        return np.around(sim_matrix, 5).tolist()


    def save_similarity_index(self, file_path):
        if self.__similarity_index:
            self.__similarity_index.save(file_path)
        else:
            return Exception(u"先计算相似性矩阵才能保存...")


    def proj_docs(self, n_components=2):
        """文档投影"""
        features = matutils.corpus2dense(self.__tfidf_corpus, num_terms=len(self.__dictionary.keys()),
                                         num_docs=len(self.corpus)).T
        proj_data = TSNE(n_components=n_components, random_state=0).fit_transform(features)
        proj_data = np.array(proj_data, dtype='float')
        # return np.around(proj_data, 5).tolist()
        return proj_data.tolist()


    def kmeans_docs(self, n_clusters=8):
        """文档聚类"""
        features = matutils.corpus2dense(self.__tfidf_corpus, num_terms=len(self.__dictionary.keys()),
                                         num_docs=len(self.corpus)).T
        db = KMeans(n_clusters=n_clusters, random_state=0).fit(features)
        return db.labels_.tolist()


    def kmeans_features(self, n_clusters=8, features=None):
        """特征聚类"""
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


    def save_dictionary(self, desc):
        self.__dictionary.save(desc)


    def save_doc2bow(self, desc):
        corpora.MmCorpus.serialize(desc, self.__bow_corpus)


    def save_tfidf_model(self, desc):
        self.__tfidf_model.save(desc)


    def lda(self, num_topics=2):
        lda = models.LdaModel(corpus=self.__tfidf_corpus, id2word=self.__dictionary, num_topics=num_topics)
        pprint.pprint(lda.print_topics(num_topics=num_topics, num_words=20))  # 把所有的主题打印出来看看


    def word_freq(self):
        """求每个词语词频并按词频降序排序"""
        frequency = defaultdict(int)
        word_docs_freq = dict() # {wordindex: {docid1: x, docid2: y, ...}}}
        for docid, doc in enumerate(self.__bow_corpus):
            for word in doc:
                frequency[word[0]] += word[1]
                docs_freq = word_docs_freq.get(word[0], dict())
                docs_freq[docid] = word[1]
                word_docs_freq[word[0]] = docs_freq
        word_freq_list = list(frequency.items())
        word_freq_list.sort(key=lambda d: d[1], reverse=True)
        return (word_freq_list, word_docs_freq)


    def word_doc_relation(self, rate_words=1):
        word_freq_list, word_docs_freq = self.word_freq()
        high_freq_words = word_freq_list[:math.floor(len(self.corpus)*rate_words)]
        r_word_doc = []
        for [wordid, sum_freq] in high_freq_words:
            docs_req = word_docs_freq.get(wordid)
            for docid, freq in docs_req.items():
                r_word_doc.append({"word": self.__dictionary[wordid], "doc":docid, "weight": freq/sum_freq})
        return r_word_doc




