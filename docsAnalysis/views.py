from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from docsAnalysis.models import Document
import os
import json
import numpy as np
from gensim import similarities
import pprint

# Create your views here.
def _read_json(file_path):
    """读取json文件，返回json对象"""
    with open(file_path, 'r', encoding='utf-8') as f:
        obj = json.loads(f.read())
    return obj

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))

similarity_index = similarities.MatrixSimilarity.load(_get_abs_path(u'output/similarity.index'))

def proj(request):
    return JsonResponse({'projlist': _read_json(_get_abs_path(u'output/proj.json'))})

def similarity(request):
    sim_list = similarity_index.similarity_by_id(1)
    sim_list = sim_list.astype(np.float)
    sim_list = np.around(sim_list, 5).tolist()

    return HttpResponse(sim_list)