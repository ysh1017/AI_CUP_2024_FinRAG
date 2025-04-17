"""Weaviate wrapper providing hybrid search."""
from __future__ import annotations
from typing import List

import weaviate
from langchain.embeddings import OpenAIEmbeddings
from ..settings import cfg, logger

class SearchHit:
    """Lightweight container for search result."""
    def __init__(self, pid: int, content: str):
        self.pid = pid
        self.content = content

class WeaviateHybridSearcher:
    """Hybrid search: dense (OpenAI) + sparse (BM25)"""
    def __init__(self, url: str | None = None):
        self.url = url or cfg.get("weaviate", "url", fallback="http://127.0.0.1:8882")
        self.client = weaviate.Client(self.url)
        self.embeddings = OpenAIEmbeddings(chunk_size=1, model="text-embedding-3-large")

    def search(self, query: str, *, pids: List[int], category: str, limit: int = 100, alpha: float = 0.8):
        query_vector = self.embeddings.embed_query(query)
        vector_str = ','.join(map(str, query_vector))
        pid_conditions = ' '.join([f'{{path: ["pid"], operator: Equal, valueText: "{pid}"}}' for pid in pids])
        namespace = {
            "finance": "Financedev",
            "insurance": "Insurancedev",
        }.get(category, "Faqdev")

        gql = f"""{{
            Get {{
                {namespace}(where: {{
                    operator: Or,
                    operands: [{pid_conditions}]
                }}, hybrid: {{
                    query: "{query}",
                    vector: [{vector_str}],
                    alpha: {alpha}
                }}, limit: {limit}) {{
                    pid
                    content
                    _additional {{ distance score }}
                }}
            }}
        }}"""
        res = self.client.query.raw(gql)
        if 'errors' in res:
            raise RuntimeError(res['errors'][0]['message'])
        hits = res['data']['Get'][namespace]
        logger.debug("weaviate hits=%d", len(hits))
        return [SearchHit(int(item['pid']), item['content']) for item in hits]
