"""
evaluation/retrieval_metrics.py - Recall@K, Precision@K, MRR (Part 6)

Gộp 3 metric vào 1 file thay vì tách recall.py, precision.py, mrr.py - mỗi 
hàm chỉ có vài dòng,tách quả nhỏ tăng số lần import qua lại mà không tăng giá trị tổ chức
. Tách biệt file chỉ có ý nghĩa khi 2 nhóm thực sự khác loại đánh giá - đó là lý do 
retrieval_metrics.py và correctness.py là 2 file riêng (retrieval quality vs generation quality)
không phải vì mỗi metric riêng lẻ
"""
from statistics import mean

from src.models import TestCase

def recall_at_k(retrieved_chunk_ids: list, relevant_chunk_ids: list) -> float:
    if not relevant_chunk_ids:
        return 0.0
    hits = sum(1 for cid in retrieved_chunk_ids if cid in set(relevant_chunk_ids))
    return hits / len(relevant_chunk_ids)

def precision_at_k(retrieved_chunk_ids: list, relevant_chunk_ids: list) -> float:
    if not retrieved_chunk_ids:
        return 0.0
    hits = sum(1 for cid in retrieved_chunk_ids if cid in set(relevant_chunk_ids))
    return hits / len(retrieved_chunk_ids)

def reciprocal_rank(retrieved_chunk_ids: list, relevant_chunk_ids: list) -> float:
    relevant = set(relevant_chunk_ids)
    for rank, cid in enumerate(retrieved_chunk_ids, start=1):
        if cid in relevant:
            return 1.0 / rank
    return 0.0

def evaluate_retrieval(test_cases: list[TestCase], retrieve_fn, top_k: int = 10) -> dict:
    """retrieve_fn: callable(query) -> list[RetrievalResult]"""
    recalls, precisions, rrs = [], [], []
    per_case = []
    for case in test_cases:
        results = retrieve_fn(case.query)[:top_k]
        retrieved_ids = [r.chunk.chunk_id for r in results]

        r = recall_at_k(retrieved_ids, case.relevant_chunk_ids)
        p = precision_at_k(retrieved_ids, case.relevant_chunk_ids)
        rr = reciprocal_rank(retrieved_ids, case.relevant_chunk_ids)

        recalls.append(r)
        precisions.append(p)
        rrs.append(rr)
        per_case.append({
            "query": case.query,
            "category": case.category,
            "recall": r,
            "precision": p,
            "reciprocal_rank": rr,
        })

    return {
        "recall@k": round(mean(recalls), 3) if recalls else 0.0,
        "precision@k": round(mean(precisions), 3) if precisions else 0.0,
        "mrr": round(mean(rrs), 3) if rrs else 0.0,
        "n_cases": len(test_cases),
        "per_case": per_case,
    }