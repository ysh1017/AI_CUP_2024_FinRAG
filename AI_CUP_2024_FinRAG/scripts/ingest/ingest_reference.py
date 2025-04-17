"""Ingest reference corpus into Weaviate."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path

import weaviate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

from esun_finrag.settings import cfg, logger

TOKEN_LIMIT = 8192

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--data', default='data/aicup_noocr_sec.json')
    p.add_argument('--config', default='cfg.ini')
    return p.parse_args()

def main():
    args = parse_args()
    cfg.read(args.config)
    client = weaviate.Client(cfg.get('weaviate','url'))
    embeddings = OpenAIEmbeddings(chunk_size=1, model='text-embedding-3-large')
    splitter = RecursiveCharacterTextSplitter(chunk_size=4096, chunk_overlap=500)
    dataset = json.loads(Path(args.data).read_text(encoding='utf-8'))
    for item in dataset:
        pid = item['pid']
        cat = item['category']
        content = item['content'] if isinstance(item['content'], str) else json.dumps(item['content'], ensure_ascii=False)
        classmap = {'finance':'Financedev','insurance':'Insurancedev','faq':'Faqdev'}
        classnm = classmap.get(cat,'Faqdev')

        if not client.schema.exists(classnm):
            schema = {
                'class': classnm,
                'properties': [{'name':'pid','dataType':['text']},
                               {'name':'content','dataType':['text'],'tokenization':'gse'}],
                'vectorizer': 'text2vec-openai',
                'moduleConfig': {'text2vec-openai': {'model': 'text-embedding-3-large', 'dimensions': 3072, 'type':'text'}}
            }
            client.schema.create_class(schema)
            logger.info('Created class %s', classnm)

        if len(content) > TOKEN_LIMIT:
            chunks = splitter.split_text(content)
        else:
            chunks = [content]
        for chunk in chunks:
            client.data_object.create({'pid':pid,'content':chunk}, classnm)
    logger.info('Ingest completed.')

if __name__ == '__main__':
    main()
