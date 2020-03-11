from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
import json
import numpy as np

from docsAnalysis.mynlp import base_analysis
from docsAnalysis.mynlp import wr_tmp_data

corpus = wr_tmp_data.load_corpus_info()

# Create your views here.
def _read_json(file_path):
    """读取json文件，返回json对象"""
    with open(file_path, 'r', encoding='utf-8') as f:
        obj = json.loads(f.read())
    return obj

def proj(request):
    # return JsonResponse({'datum': _read_json(_get_abs_path(u'output/nCovMemory/proj.json'))})
    pass

def similarity(request):
    pass

def extra_keywords_by_id(request):
    """根据文档id抽取关键词"""
    params = request.GET
    keywords = base_analysis.extra_keywords_by_id(corpus, docid=int(params.get('id')), n_min=params.get('n_min', 5), ratio=params.get('ratio', 0.05), with_weight=params.get('with_weight', False))
    return JsonResponse({'datum': keywords})


def get_common_keywords(request):
    """抽取文档的公共关键词"""
    params = request.GET
    keywords = base_analysis.get_common_keywords(corpus, id1=int(params.get('id1')), id2=int(params.get('id2')))
    return JsonResponse({'datum': keywords})


def get_common_words(request):
    """获取两个文档的公共词"""
    params = request.GET
    common_words = base_analysis.get_common_words(corpus, int(params.get('id1')), int(params.get('id2')))
    return JsonResponse({'datum': common_words})


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