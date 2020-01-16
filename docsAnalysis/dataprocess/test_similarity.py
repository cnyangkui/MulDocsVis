# -*- encoding: utf-8 -*-
import os
from gensim import similarities
import pprint


index = similarities.MatrixSimilarity.load(u'../output/similarity.index')
id = index.similarity_by_id(0).tolist()
print(type(id))
