# -*- encoding: utf-8 -*-
import numpy as np
import pandas as pd
import json
import pprint
from sklearn.metrics.pairwise import pairwise_distances

from docsAnalysis.mynlp import wr_tmp_data
from docsAnalysis.mynlp import base_analysis


class Node(object):

    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left  # 左子聚类
        self.right = right  # 右子聚类
        self.vec = vec  # 聚类的中心点
        self.id = id  # 聚类的id
        self.distance = distance  # 左右子聚类间的距离（相似度）

    def __str__(self):
        return "%s" % (self.id)


class HierarchicalTree(object):
    # 根据数据集形成聚类树
    def construct(self, rows):
        distance_set = {}  # 用distance_set来缓存距离最小的计算值
        current_node_id = -1

        # 最开始聚类就是数据集中的行，每行一个聚类
        nodes = [Node(rows[i], id=i) for i in
                 range(len(rows))]  # 原始集合中的聚类都设置了不同的正数id，（使用正数是为了标记这是一个叶节点）（使用不同的数是为了建立配对集合）

        while len(nodes) > 1:
            lowest_pair = (0, 1)
            closest = self.cosine_distance(nodes[0].vec, nodes[1].vec)

            # 遍历每一对聚类，寻找距离最小的一对聚类
            for i in range(len(nodes) - 1):
                for j in range(i + 1, len(nodes)):
                    if (nodes[i].id, nodes[j].id) not in distance_set:
                        distance_set[(nodes[i].id, nodes[j].id)] = self.cosine_distance(nodes[i].vec, nodes[j].vec)
                    d = distance_set[(nodes[i].id, nodes[j].id)]

                    if d < closest:
                        closest = d
                        lowest_pair = (i, j)

            # 计算距离最近的两个聚类的平均值作为代表新聚类的中心点
            merged_vec = [(nodes[lowest_pair[0]].vec[i] + nodes[lowest_pair[1]].vec[i]) / 2.0 for i in
                          range(len(nodes[0].vec))]

            # 将距离最近的两个聚类合并成新的聚类
            new_node = Node(merged_vec, left=nodes[lowest_pair[0]],
                            right=nodes[lowest_pair[1]],
                            distance=float(closest), id=current_node_id)

            # 不再原始集合中的聚类id设置为负数。为了标记这是一个枝节点
            current_node_id -= 1
            pprint.pprint(current_node_id)
            # 删除旧的聚类。（因为旧聚类已经添加为新聚类的左右子聚类了）
            del nodes[lowest_pair[1]]
            del nodes[lowest_pair[0]]
            nodes.append(new_node)

        return nodes[0]  # 返回聚类树

    def cosine_distance(self, vec1, vec2):
        if np.sum(vec1) == 0 or np.sum(vec2) == 0:
            return 1.0
        return 1.0 - np.dot(vec1, vec2) / (np.linalg.norm(vec1) * (np.linalg.norm(vec2)))


def write_json(obj, desc, indent=None):
    """将对象写入json文件"""
    with open(desc, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, default=lambda obj: obj.__dict__, ensure_ascii=False, indent=indent)


if __name__ == '__main__':
    corpus = wr_tmp_data.load_corpus_base_info()
    matrix = pd.DataFrame(corpus['similarity'])
    pprint.pprint(matrix)
    df = pd.DataFrame(base_analysis.build_tfidf_vsm(corpus))
    vsm = df.values
    dist = pd.DataFrame(pairwise_distances(df, metric="cosine"))
    dist = dist.round(6)
    pprint.pprint(dist)

    tree = HierarchicalTree()
    res = tree.construct(vsm)
    pprint.pprint(res)

    # shape = vsm.shape
    # for i in range(shape[0]):
    #     if np.sum(vsm[i]) == 0:
    #         print(i)
