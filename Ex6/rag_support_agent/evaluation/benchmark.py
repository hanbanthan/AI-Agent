"""
evaluation/benchmark.py - so sánh experiment A/B/C/D trên eval dataset

Tách riêng khỏi main.py có chủ đích: benchmark.py trả lời "hệ thống 
đang tối tới đâu, method nào tốt hơn" (chạy đánh giá hàng loạt);
main.py trả lời "tả lời 1 câu hỏi cụ thể của user" (chạy pipeline 
thật). 2 mục đích khác nhau, không nên gộp vào 1 script.
"""

import functools

from evaluation.retrieval_metrics import evaluate_retrieval
from src.rag_pipeline import retrieve_by_method

def run_benchmark(eval_cases, vector_store, bm25_store, top_k: int = 5) -> dict:
    methods = {
        "A: vector": functools.partial(retrieve_by_method, vector_store=vector_store, bm25_store=bm25_store, method="vector"),
        "B: bm25": functools.partial(retrieve_by_method, vector_store=vector_store, bm25_store=bm25_store, method="bm25"),
        "C: hybrid": functools.partial(retrieve_by_method, vector_store=vector_store, bm25_store=bm25_store, method="hybrid"),
    }

    # Experiment D (hybrid + rerank) đo Recall/Precision/MRR trên TOP CANDIDATE
    # trước rerank thì không khác Experiment C ở tầng retrieval — giá trị của
    # reranker nằm ở THỨ TỰ trong top-N cuối, nên D nên được đo bằng
    # Answer Correctness/Faithfulness (evaluation/correctness.py) qua
    # full pipeline, không phải qua evaluate_retrieval() ở đây.

    table = {}
    for name, fn in methods.items():
        table[name] = evaluate_retrieval(eval_cases, fn, top_k=top_k)
    return table

def print_benchmark_results(table: dict):
    print(f"{'Method':<14}{'Recall@K':>10}{'Precision@K':>14}{'MRR':>8}")
    print("-" * 48)
    for name, m in table.items():
        print(f"{name:<14}{m['recall@k']:>10}{m['precision@k']:>14}{m['mrr']:>8}")

def main():
    import config
    from src.ingestion import load_documents
    from src.chunking import chunk_documents
    from src.vector_store import VectorStore
    from src.bm25 import BM25Store
    from evaluation.dataset import build_eval_dataset

    docs = load_documents(config.DATA_DIR, config.SUPPORT_DOCS_DIR, config.TICKETS_DIR)
    chunks = chunk_documents(docs, chunk_size=config.CHUNK_SIZE, overlap_ratio=config.CHUNK_OVERLAP_RATIO)
    vector_store = VectorStore.build(chunks)
    bm25_store = BM25Store.build(chunks)
    eval_cases = build_eval_dataset(chunks)

    print(f"Loaded {len(docs)} documents -> {len(chunks)} chunks "
          f"(chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP_RATIO})")
    print(f"Eval dataset: {len(eval_cases)} test cases\n")

    table = run_benchmark(eval_cases, vector_store, bm25_store, top_k=5)
    print_benchmark_results(table)

if __name__ == "__main__":
    main()