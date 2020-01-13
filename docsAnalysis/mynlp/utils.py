# -*- encoding: utf-8 -*-
import os
import json


def read_corpus(file_path):
    """读取语料库"""
    docs = []
    files = os.listdir(file_path)
    for file in files:
        with open(os.path.join(file_path, file), 'r', encoding='utf-8', errors='ignore') as f:
            docs.append(f.read())
    return docs


def write_json(obj, desc):
    """将对象写入json文件"""
    with open(desc, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, ensure_ascii=False)
