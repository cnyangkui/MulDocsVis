from sklearn import datasets
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram
import pprint

from docsAnalysis.mynlp import wr_tmp_data
from docsAnalysis.mynlp import base_analysis

corpus = wr_tmp_data.load_corpus_base_info()

data = base_analysis.build_tfidf_vsm(corpus)
# df = pd.DataFrame(data)
# min_max_scaler = preprocessing.MinMaxScaler()
# data_M = min_max_scaler.fit_transform(data)
# data = np.round(data, 5)
# pprint.pprint(data_M)


plt.figure(figsize=(20,6))
Z = linkage(data, method='average', metric='cosine') #cityblock,euclidean
pprint.pprint(Z)
pprint.pprint(Z.shape)
p = dendrogram(Z, 0)
plt.show()

