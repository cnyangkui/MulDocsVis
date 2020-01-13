# -*- encoding: utf-8 -*-
import sys
import os
import django

# 这两行很重要，用来寻找项目根目录，os.path.dirname要写多少个根据要运行的python文件到根目录的层数决定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(BASE_DIR)
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MulDocsVis.settings')
django.setup()

from docsAnalysis.models import Document, DocSim


def import_doc_content(file_path):
    """向数据库中插入文档内容
    :param file_path: str, 文本数据所在文件夹，文档内容单独存储，一个文件对应一篇文档
    """
    docs = []
    files = os.listdir(file_path)
    for index, file in enumerate(files):
        with open(os.path.join(file_path, file), 'r', encoding='utf-8', errors='ignore') as f:
            doc = Document(did=index, content=f.read())
            doc.save()

if __name__ == '__main__':
    import_doc_content(u'Y:/yk-file/文本数据/THUCNews/财经5000')