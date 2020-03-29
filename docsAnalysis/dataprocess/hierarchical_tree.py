import math
from queue import Queue
from scipy.cluster.hierarchy import linkage, dendrogram
import pprint

from docsAnalysis.mynlp import wr_tmp_data
from docsAnalysis.mynlp import base_analysis
from docsAnalysis.dataprocess import utils

corpus = wr_tmp_data.load_corpus_base_info()
# data = base_analysis.build_tfidf_vsm(corpus)
# print(data.shape)

def generate_tree(corpus):
    data = base_analysis.build_tfidf_vsm(corpus)
    length = len(data)
    Z = linkage(data, method='average', metric='cosine')  # cityblock, euclidean
    rows = Z.shape[0]
    nodes = list()
    for i in range(length):
        nodes.append({'name': i})
    for index, row in enumerate(Z):
        n1, n2 = int(row[0]), int(row[1])
        print(index, n1, n2, len(nodes))
        key = rows + index + 1
        new_node = {
            'name': key,
            'distance': round(row[2], 6),
            'size': row[3],
            'children': [
                nodes[n1], nodes[n2]
            ]
        }
        nodes.append(new_node)
    return nodes[-1]


def optimize_tree(root, n_layer):
    # 添加parent属性
    queue = Queue()
    queue.put(root)
    root['layer'] = math.ceil(root['distance'] * n_layer)
    while not queue.empty():
        node = queue.get()
        if 'children' in node:
            left = node['children'][0]
            if 'distance' in left:
                left['layer'] = math.ceil(left['distance'] * n_layer)
            else:
                left['layer'] = n_layer
            left['parent'] = node
            queue.put(left)
            right = node['children'][1]
            if 'distance' in right:
                right['layer'] = math.ceil(right['distance'] * n_layer)
            else:
                right['layer'] = n_layer
            right['parent'] = node
            queue.put(right)
    optimize_tree_core(root['children'][0], n_layer)
    optimize_tree_core(root['children'][1], n_layer)
    # 删除parent属性
    queue = Queue()
    queue.put(root)
    while not queue.empty():
        node = queue.get()
        if 'size' in node:
            del node['size']
        if 'parent' in node:
            del node['parent']
        if 'distance' in node:
            del node['distance']
        if 'children' in node:
            for child in node['children']:
                queue.put(child)
    return root


def optimize_tree_core(root, n_layer):
    if 'children' not in root:
        return
    parent = root['parent']
    # parent_dist = math.floor(parent['distance'] * n_layer)
    # dist = math.floor(root['distance'] * n_layer)
    left = root['children'][0]
    right = root['children'][1]
    if parent['layer'] == root['layer']:
        parent['children'].remove(root)
        left['parent'] = parent
        right['parent'] = parent
        parent['children'].extend(root['children'])
        optimize_tree_core(left, n_layer)
        optimize_tree_core(right, n_layer)
    else:
        optimize_tree_core(left, n_layer)
        optimize_tree_core(right, n_layer)


def level_order(root, threshold):
    queue = Queue()
    queue.put(root)
    subtrees = []
    while not queue.empty():
        node = queue.get()
        if node.get('children', list()):
            for child in node['children']:
                if child.get('distance', 1) > threshold:
                    queue.put(child)
                else:
                    subtrees.append(child)
    return subtrees


# root = generate_tree(corpus)
# utils.write_json(root, '../output/nCovMemory/htree.json')

# root = utils.read_json(u'../output/nCovMemory/htree.json')
# subtrees = level_order(root, 0.8)
# subtrees = list(filter(lambda d: d['size']>2, subtrees))
# for tree in subtrees:
#     print(tree)
# print(len(subtrees))
# pprint.pprint(root)

# optimize_tree(root, 5)
