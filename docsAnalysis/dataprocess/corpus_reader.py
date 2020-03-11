# -*- encoding: utf-8 -*-
import csv
import os

def read_corpus(file_path):
    """读取语料库"""
    docs = []
    files = os.listdir(file_path)
    for file in files:
        with open(os.path.join(file_path, file), 'r', encoding='utf-8', errors='ignore') as f:
            docs.append(f.read())
    return docs

def read_nCovMemory_corpus():
    file_path = '../crawler/nCovMemory.csv'
    docs = []
    with open(file_path, 'r', encoding='gbk') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            docs.append(row['text'])
    return docs