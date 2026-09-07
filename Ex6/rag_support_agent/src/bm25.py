"""
bm25.py - lexical/keyword retrieval (Experiment B trong bài 6)

Mạnh với mã lỗi, version, ticket ID, exact phrase - những chi tiết
chính xác mà vector search (semantic) dễ làm mờ (xem part 4)
"""

from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from .models import Chunk, RetrievalResult

def _tokenize(text: str) -> list[str]:
    return text.lower().split()

@dataclass
class BM25Store:
    bm25: BM25Okapi
    chunks: list[Chunk]

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "BM25Store":
        tokenized_corpus = [_tokenize(c.text) for c in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        return cls(bm25=bm25, chunks=chunks)

    def search(self, query: str, top_k: int = 25) -> list[RetrievalResult]:
        tokenized_query = _tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        ranked_idx = scores.argsort()[::-1][:top_k]
        return [
            RetrievalResult(chunk=self.chunks[i], score=float(scores[i]), method="bm25")
            for i in ranked_idx
            if scores[i] > 0
        ]
