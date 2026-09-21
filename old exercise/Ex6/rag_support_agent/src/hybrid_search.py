"""
hybrid_search.py - Reciprocal Rank Fusion (RRF), experiment C trong bai 6

RRF dùng thứ hạng thay vì điểm số thô để kết hợp với vector_store (cosine
similarity 0-1) và bm25 (score không giới hạn) - 2 thang đo khác nhau
hoàn toàn nên không thể cộng trực tiếp mà không chuẩn hóa. RFF né vấn đề này bằng cách chỉ quan tâm thứ hạng,
không quan tâm giá trị điểm số thô

    score(chunk) = sum (1 / (k_rrf + rank)) trên mọi danh sách chunk đó xuất hiện
"""

from .bm25 import BM25Store
from .models import RetrievalResult
from .vector_store import VectorStore

def hybrid_search(
    query: str,
    vector_store: VectorStore,
    bm25_store: BM25Store,
    top_k: int = 25,
    k_rrf: int = 60,
) -> list[RetrievalResult]:
    v_results = vector_store.search(query, top_k=top_k)
    b_results = bm25_store.search(query, top_k=top_k)

    fused_scores: dict[str, float] = {}
    chunk_lookup = {}
    for rank, r in enumerate(v_results):
        fused_scores[r.chunk.chunk_id] = fused_scores.get(r.chunk.chunk_id, 0.0) + 1.0 / (k_rrf + rank + 1)
        chunk_lookup[r.chunk.chunk_id] = r.chunk
    for rank, r in enumerate(b_results):
        fused_scores[r.chunk.chunk_id] = fused_scores.get(r.chunk.chunk_id, 0.0) + 1.0 / (k_rrf + rank + 1)
        chunk_lookup[r.chunk.chunk_id] = r.chunk

    ranked = sorted(fused_scores.items(), key=lambda x: -x[1], reverse=True)[:top_k]
    return [
        RetrievalResult(chunk=chunk_lookup[chunk_id], score=score, method="hybrid") 
        for chunk_id, score in ranked
    ]
