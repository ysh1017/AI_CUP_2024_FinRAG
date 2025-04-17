"""Retriever orchestrating hybrid search and VoyageAI rerank."""
from __future__ import annotations
from typing import List

from voyageai import Client as VoyageClient

from .datastore.weaviate_client import WeaviateHybridSearcher
from .settings import cfg, logger

class Retriever:
    """Return PID with highest relevance score."""
    def __init__(self, voyage_key: str | None = None, weaviate_url: str | None = None):
        key = voyage_key or cfg.get("voyage", "api_key", fallback="")
        self.voyage = VoyageClient(api_key=key)
        self.searcher = WeaviateHybridSearcher(url=weaviate_url)

    def top1(self, query: str, *, pids: List[int], category: str) -> int:
        hits = self.searcher.search(query, pids=pids, category=category, limit=100)
        docs = [h.content for h in hits]
        reranked = self.voyage.rerank(query, docs, model="rerank-2", top_k=1)
        best_idx = reranked.results[0].index
        pid = hits[best_idx].pid
        logger.debug("top pid=%s score=%.3f", pid, reranked.results[0].relevance_score)
        return pid
