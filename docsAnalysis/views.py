from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
import json
import numpy as np

from docsAnalysis import models
from docsAnalysis.mynlp import base_analysis
from docsAnalysis.mynlp import wr_tmp_data
from docsAnalysis.dataprocess import utils
from docsAnalysis.dataprocess import hierarchical_tree

corpus = wr_tmp_data.load_corpus_base_info()

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))


# Create your views here.
def proj(request):
    # return JsonResponse({'datum': _read_json(_get_abs_path(u'output/nCovMemory/proj.json'))})
    pass


def similarity(request):
    pass


def extra_keywords_by_id(request):
    """根据文档id抽取关键词"""
    params = request.GET
    keywords = base_analysis.extra_keywords_by_id(corpus, docid=int(params.get('id')), n_min=params.get('n_min', 5),
                                                  ratio=params.get('ratio', 0.05),
                                                  with_weight=params.get('with_weight', False))
    return JsonResponse({'datum': keywords})


def get_keywords(request):
    """抽取文档的公共关键词"""
    params = request.GET
    # 使用根据数据集构造的TF-IDF模型抽取关键词
    ids = params.getlist('ids', list())
    switch = {
        "single": lambda ids, topK, ratio, withWeight: base_analysis.extra_keywords_by_id(corpus, id=ids[0],
                                                                                            topK=topK, ratio=ratio,
                                                                                            withWeight=withWeight),
        "multiple": lambda ids, topK, ratio, withWeight: base_analysis.get_common_keywords(corpus, ids=ids,
                                                                                             withWeight=withWeight,
                                                                                             ratio=ratio),
        "doc2keywords": lambda ids, topK, ratio, withWeight: base_analysis.get_keywords_by_ids(corpus, ids=ids,
                                                                                             topK=topK)
    }
    type = params['type']
    keywords = switch[type](params.getlist('ids'),
                            int(params.get('topK', 20)), float(params.get('ratio', 0.05)), params.get('withWeight'))

    # 使用jieba抽取关键词
    # ids = params.getlist('ids', list())
    # docs = list()
    # for id in ids:
    #     doc = models.Document.objects.values('content').get(pk=int(id))
    #     docs.append(doc['content'])
    # switch = {
    #     "single": lambda docs, topK, withWeight: base_analysis.jieba_extra_keywords_from_doc(sentence=docs[0],
    #                                                                                          topK=topK,
    #                                                                                          withWeight=withWeight),
    #     "multiple": lambda docs, topK, withWeight: base_analysis.jieba_extra_keywords_from_docs(sentences=docs,
    #                                                                                           topK=topK),
    #     "bigdoc": lambda docs, topK, withWeight: base_analysis.jieba_extra_keywords_from_bigdoc(sentences=docs,
    #                                                                                             topK=topK,
    #                                                                                             withWeight=withWeight)
    # }
    # type = params['type']
    # keywords = switch[type](docs, int(params.get('topK', 50)), params.get('withWeight', False))

    return JsonResponse({
        'code': 0,
        'message': 'success',
        'data': {
            'keywords': keywords
        }
    })


def get_common_words(request):
    """获取两个文档的公共词"""
    params = request.GET
    common_words = base_analysis.get_common_words(corpus, ids=params.getlist('ids'))
    return JsonResponse({
        'code': 0,
        'message': 'success',
        'data': {
            'commonWords': common_words
        }
    })


def similarity_by_id(request):
    """获取一个文档与其它所有文档的相似度"""
    params = request.GET
    res = base_analysis.similarity_by_id(corpus, id=int(params.get('id')))
    return JsonResponse({'datum': res})


def similarity_by_ids(request):
    """获取两个文档间的相似度"""
    params = request.GET
    res = base_analysis.similarity_by_ids(corpus, id1=int(params.get('id1')), id2=int(params.get('id2')))
    return JsonResponse({'datum': res})


def get_htree(request):
    root = utils.read_json(_get_abs_path(u'output/nCovMemory/htree.json'))
    # root = hierarchical_tree.optimize_tree(root, 5)
    return JsonResponse({
        'code': 0,
        'message': 'success',
        'data': root
    })


def get_docs(request):
    params = request.GET
    ids = params.getlist('ids', list())
    ids = [int(id) for id in ids]
    print(ids)
    docs = models.Document.objects.values('did', 'content').filter(pk__in=ids)
    docs = list(docs)
    if docs:
        return JsonResponse({
            'code': 0,
            'message': 'success',
            'data': {
                'texts': docs
            }
        })
    else:
        return JsonResponse({
            'code': 404,
            'message': '找不到...',
        })


def get_optimized_tree(request):
    tree_data = utils.read_json(_get_abs_path(u'output/nCovMemory/htree.json'))
    tree_data = hierarchical_tree.optimize_tree(tree_data, 10)
    # subtrees = hierarchical_tree.level_order(tree_data, 1)
    return JsonResponse({
        'code': 0,
        'message': 'success',
        'data': tree_data
    })
