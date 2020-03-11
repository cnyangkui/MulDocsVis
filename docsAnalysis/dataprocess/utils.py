# -*- encoding: utf-8 -*-
import os
import json
import csv

def write_json(obj, desc, indent=None):
    """将对象写入json文件"""
    with open(desc, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, ensure_ascii=False, indent=indent)

def write_csv(desc, obj):
    fieldnames = obj[0].keys()
    print(fieldnames)
    with open(desc, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for o in obj:
            writer.writerow(o)