# processing/semantic/embeddings.py
from functools import lru_cache
from typing import List

from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    def __init__(self):
        self.model = OpenAIEmbeddings(model="text-embedding-3-large")

    @lru_cache(maxsize=50_000)
    def embed_one(self, text: str) -> tuple[float, ...]:
        return tuple(self.model.embed_query(text))

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        # cache-aware batching
        vectors = []
        for t in texts:
            vectors.append(list(self.embed_one(t)))
        return vectors
