import csv

from docsAnalysis.crawler import html_extractor

def spider(src, desc):
    fieldnames = ['id', 'category', 'media', 'date', 'title', 'text']
    with open(desc, 'a', encoding='gbk', newline='', errors='ignore') as wf:
        csv_writer = csv.writer(wf, dialect='excel')
        csv_writer.writerow(fieldnames)
        with open(src, 'r', encoding='gbk') as rf:
            csv_reader = csv.DictReader(rf)
            for row in csv_reader:
                text = html_extractor.extract(row['url'])
                if text == None:
                    text = html_extractor.extract(row['archive'])
                if text == None:
                    continue
                csv_writer.writerow([row['id'], row['category'], row['media'], row['date'], row['title'], text])

if __name__ == '__main__':
    spider('data_gbk.csv', 'nCovMemory.csv')