import jieba
import jieba.posseg
import os

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.path.dirname(__file__), path))
jieba.load_userdict(_get_abs_path("dict.txt"))
seg_list = jieba.posseg.cut('''一切都因新型冠状病毒疫情而起，因深处武汉耳闻目睹而思考深刻，我试着重新理解生命和生活。''')

for i in seg_list:
    print(i)