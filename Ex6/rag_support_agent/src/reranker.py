"""
reranker.py - Experiment D: rerank candidate pool bằng cross-encoder

STAND-IN: cross-encoder thật (ms-macro-MiniLM, BGE-reranker...) cần tải
model từ HuggingFace - không khả dụng trong sandbox này. `rerank()` dùng
1 "toy scorer" (TF-IDF similarity + keyword overlap) để mô phỏng hành vi
"xem xét tương tác trực tiếp giữa query và document" - không phải
cross-encoder thật. Khi lên production, thay `_toy_cross_encoder_scorer` 
bằng model thật; interface `rerank(query, candidate, top_n)` giữ nguyên.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import RetrievalResult

def _toy_cross_encoder_score(query: str, text: str) -> float:
    vectorizer = TfidfVectorizer().fit([query, text])
    vecs = vectorizer.transform([query, text])
    sim = cosine_similarity(vecs[0], vecs[1])[0][0]

    q_terms = set(query.lower().split())
    t_terms = set(text.lower().split())
    overlap_ratio = len(q_terms & t_terms) / max(1, len(q_terms))

    return 0.6 * sim + 0.4 * overlap_ratio

def rerank(query: str, candidates: list[RetrievalResult], top_n: int = 5) -> list[RetrievalResult]:
    scored = [
        RetrievalResult(
            chunk=r.chunk,
            score=_toy_cross_encoder_score(query, r.chunk.text),
            method="rerank"
        )
        for r in candidates
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_n]
