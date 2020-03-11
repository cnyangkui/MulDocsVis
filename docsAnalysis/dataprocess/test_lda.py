from gensim.test.utils import common_texts, common_corpus
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import pprint

# Create a corpus from a list of texts
texts = [['褒贬','春秋','看重','德望','孔子'],
        ['慈禧','政治','果断','胆识','眼光','改革'],
        ['历史','兴替','唐朝'],
        ['食堂','饭菜','不好吃','闹肚子', '便宜'],
        ['就餐','挑剔','新鲜','美味','蜜桃','西瓜'],
         ['苹果', '梨子','价格','便宜'],
         ['奥迪', '大众', '汽车', '价格', '昂贵', '买不起']]

# pprint.pprint(common_texts)

dct = Dictionary(texts)
corpus = [dct.doc2bow(text) for text in texts]

lda = LdaModel(corpus, num_topics=3, id2word=dct)
# Print the most contributing words for 2 topics
res = lda.print_topics(num_topics=3, num_words=6)

pprint.pprint(res)