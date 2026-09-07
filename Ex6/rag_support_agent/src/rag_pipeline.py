"""
rag_pipeline.py - lắp toàn bộ Online Query Pipeline (part 2) , chọn 
Experiment A/B/C/D qua tham số `method`
"""

from .bm25 import BM25Store
from .context_builder import build_context, detect_conflicts
from .llm import generate_answer, Answer
from .metadata_filter import filter_chunks
from .models import RetrievalResult
from .reranker import rerank 
from .vector_store import VectorStore
from .hybrid_search import hybrid_search

def retrieve_by_method(
    query: str,
    method: str,
    vector_store: VectorStore,
    bm25_store: BM25Store,
    top_k: int = 25,
) -> list[RetrievalResult]:
    if method == "vector":
        return vector_store.search(query, top_k=top_k)
    if method == "bm25":
        return bm25_store.search(query, top_k=top_k)
    if method in ("hybrid", "hybrid_rerank"):
        return hybrid_search(query, vector_store, bm25_store, top_k=top_k)
    raise ValueError(f"Unknown retrieval method: {method}")

def run_rag_pipeline(
    query: str,
    vector_store: VectorStore,
    bm25_store: BM25Store,
    method: str = "hybrid_rerank",
    access_level: str = "public",
    top_k: int = 25,
    rerank_top_n: int = 5,
    context_word_budget: int = 300,
    llm_fn = None,
) -> dict:
    """method: "vector" | "bm25" | "hybrid" | "hybrid_rerank" - Experiment A/B/C/D"""

    candidates = retrieve_by_method(query, method, vector_store, bm25_store, top_k=top_k)

    # metadata filter (pre-filter)
    allowed_chunks_ids = {
        c.chunk_id for c in filter_chunks(
            [c.chunk for c in candidates],
            access_level=access_level,
        )
    }  
    candidates = [c for c in candidates if c.chunk.chunk_id in allowed_chunks_ids]

    if method == "hybrid_rerank":
        top_results = rerank(query, candidates, top_n=rerank_top_n)
    else:
        top_results = candidates[:rerank_top_n]

    context = build_context(top_results, word_budget=context_word_budget)
    has_conflict = detect_conflicts(top_results)

    answer: Answer = generate_answer(query, context, llm_fn=llm_fn)

    return {
        "query": query,
        "method": method,
        "retrieved_chunk_ids": [c.chunk.chunk_id for c in candidates],
        "final_chunk_ids": [c.chunk.chunk_id for c in top_results],
        "context": context,
        "context_has_conflict": has_conflict,
        "answer": answer.text,
        "cited_doc_ids": answer.cited_doc_ids,
    }

