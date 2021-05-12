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
from docsAnalysis.mynlp.sentimentAnalysis import DocSentimentAnalysis

if __name__ == '__main__':
    handler = DocSentimentAnalysis.Sentimentor()
    allDocs = Document.objects.all().values('content')
    for doc in allDocs:
        doc_sentiment_score = handler.doc_sentiment_score(doc['content'])
        print(doc_sentiment_score)