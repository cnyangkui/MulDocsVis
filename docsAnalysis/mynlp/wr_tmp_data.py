# -*- encoding: utf-8 -*-
from gensim import corpora, models, similarities
import pprint
import os

from docsAnalysis.mynlp import mycorpus
from docsAnalysis.dataprocess import corpus_reader

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))

def write_corpus_base_info(all_docs):
    # 分词处理
    corpus = mycorpus.Corpus(all_docs)
    corpus.set_tokenize_config(min_freq=5)
    corpus.tokenize()
    pprint.pprint("分词结束...")

    # 计算文档相似性矩阵
    corpus.cal_similarity_matrix()
    corpus.save_similarity_index(_get_abs_path('tmp/similarity.index'))
    pprint.pprint("计算相似性矩阵...")

    # 保存词典
    corpus.save_dictionary(_get_abs_path('tmp/dictionary.dict'))
    pprint.pprint("保存词典...")

    # 保存词袋
    corpus.save_doc2bow(_get_abs_path('tmp/doc2bow.mm'))
    pprint.pprint("保存词袋...")

    # 保存 tfidf model
    corpus.save_tfidf_model(_get_abs_path('tmp/tfidfmodel.model'))
    pprint.pprint("保存 tfidf model...")


def load_corpus_base_info():
    # 加载词表
    dictionary = corpora.Dictionary.load(_get_abs_path('tmp/dictionary.dict'))
    # 加载词典向量
    corpus = corpora.MmCorpus(_get_abs_path('tmp/doc2bow.mm'))
    # 加载模型
    tfidf_model = models.TfidfModel.load(_get_abs_path('tmp/tfidfmodel.model'))
    # 加载相似度计算索引
    similarity = similarities.Similarity.load(_get_abs_path('tmp/similarity.index'))
    tfidf_corpus = tfidf_model[corpus]
    return {
        "dictionary": dictionary,
        "doc2bow": corpus,
        "tfidfmodel": tfidf_model,
        "tfidfcorpus": tfidf_corpus,
        "similarity": similarity,
    }

# all_docs = corpus_reader.read_nCovMemory_corpus()
# write_corpus_base_info(all_docs)