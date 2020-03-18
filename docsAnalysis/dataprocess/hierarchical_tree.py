from scipy.cluster.hierarchy import linkage, dendrogram
import pprint

from docsAnalysis.mynlp import wr_tmp_data
from docsAnalysis.mynlp import base_analysis
from docsAnalysis.dataprocess import utils

corpus = wr_tmp_data.load_corpus_base_info()

data = base_analysis.build_tfidf_vsm(corpus)
length = len(data)
Z = linkage(data, method='average', metric='cosine') # cityblock, euclidean
rows = Z.shape[0]
nodes = list()
for i in range(length):
    nodes.append({'name': i})
for index, row in enumerate(Z):
    n1, n2 = int(row[0]), int(row[1])
    print(index, n1, n2, len(nodes))
    key = rows + index + 1
    new_node = {'name': key, 'children': [
        nodes[n1], nodes[n2]
    ]}
    nodes.append(new_node)
utils.write_json(nodes[-1], 'htree.json')
