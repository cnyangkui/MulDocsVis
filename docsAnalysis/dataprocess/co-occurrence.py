# -*- encoding: utf-8 -*-
from collections import defaultdict
import csv
import pprint

from docsAnalysis.mynlp import mycorpus


def read_nCovMemory(file_path):
    """
    读取疫情文本数据
    """
    docs = []
    with open(file_path, 'r', encoding='gbk') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            docs.append(row['text'])
    return docs


def get_corpus(all_docs):
    corpus = mycorpus.Corpus(all_docs)
    corpus.set_tokenize_config(min_freq=2)
    corpus.tokenize()
    pprint.pprint("分词结束...")
    return corpus


def n_gram(corpus: mycorpus.Corpus, ngram=5, min_freq=5):
    tokenized_docs = corpus.tokenized_docs
    token2id = corpus.dictionary.token2id
    frequency = defaultdict(int)
    for doc in tokenized_docs:
        for i in range(len(doc)-ngram):
            for j in range(i + 1, i + ngram):
                if doc[i] != doc[j]:
                    id1, id2 = token2id[doc[i]], token2id[doc[j]]
                    if id1 < id2:
                        frequency[str(id1) + ',' + str(id2)] += 1
                    else:
                        frequency[str(id2) + ',' + str(id1)] += 1
    res = []
    for k, v in frequency.items():
        if v >= min_freq:
            temp = k.split(',')
            res.append(
                {'Source': corpus.dictionary[int(temp[0])], 'Target': corpus.dictionary[int(temp[1])], 'Weight': v})
    return res

file_path = '../crawler/nCovMemory.csv'
all_docs = read_nCovMemory(file_path)
corpus = get_corpus(all_docs)
res = n_gram(corpus)

with open(u'../output/nCovMemory/ngram.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = ['Source', 'Target', 'Weight']
    csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
    csv_writer.writeheader()
    for row in res:
        csv_writer.writerow(row)