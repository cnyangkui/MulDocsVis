# -*- encoding: utf-8 -*-
import sys
import os
import django
import json

# 这两行很重要，用来寻找项目根目录，os.path.dirname要写多少个根据要运行的python文件到根目录的层数决定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MulDocsVis.settings')
django.setup()

from docsAnalysis.models import Document


def _read_json(file_path):
    """读取json文件，返回json对象"""
    with open(file_path, 'r', encoding='utf-8') as f:
        obj = json.loads(f.read())
    return obj


def import_doc_content(file_path):
    """向数据库中插入文档内容
    :param file_path: str, 文本数据所在文件夹，文档内容单独存储，一个文件对应一篇文档
    """
    files = os.listdir(file_path)
    for index, file in enumerate(files):
        with open(os.path.join(file_path, file), 'r', encoding='utf-8', errors='ignore') as f:
            doc = Document(did=index, content=f.read())
            doc.save()


def import_doc_proj(file_path):
    """向数据库Document类中插入投影坐标
    :param file_path: str, 投影json文件
    """
    proj_data = _read_json(file_path)
    for index, value in enumerate(proj_data):
        doc = Document.objects.get(pk=index)
        doc.proj = str(value[0]) + ',' + str(value[1])
        doc.save()


def import_doc_keywords(file_path):
    keywords = _read_json(file_path)
    for index, words in enumerate(keywords):
        doc = Document.objects.get(pk=index)
        doc.keywords = ','.join(words)
        doc.save()


# def import_docsim(file_path):
#     sim_matrix = _read_json(file_path)
#     [n_row, n_col] = [len(sim_matrix), len(sim_matrix[0])]
#     for i in range(0, n_row):
#         for j in range(i + 1, n_col):
#             doc1 = Document.objects.get(pk=i)
#             doc2 = Document.objects.get(pk=j)
#             docsim = DocSimilarity(doc1=doc1, doc2=doc2, similarity=sim_matrix[i][j])
#             docsim.save()


if __name__ == '__main__':
    import_doc_content(u'Y:/yk-file/文本数据/THUCNews/财经5000')
    import_doc_proj(u'../output/proj.json')
    import_doc_keywords(u'../output/keywords.json')
    # import_docsim(u'../output/sim_matrix.json')
