"""
main.py - entry point: build toàn bộ pipeline từ dữ liệu thật trong data/,
rồi trả lời vài câu hỏi cụ thể qua experiement D (hybrid + rerank)

Muốn so sánh 4 experiment (đánh giá hệ thống, không phải trả lời 1 câu hỏi)
-> chạy `python -m evaluation.benchmark` logic riêng, xem
evaluation/benchmark.py.

Chay python main.py

"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT)) # cho phép `import evaluation.aaa`
sys.path.insert(0, str(ROOT / "src")) # cho phép `import models`, `import rag_pipeline`

import config
from src.chunking import chunk_documents
from src.ingestion import load_documents
from src.vector_store import VectorStore
from src.bm25 import BM25Store
from src.rag_pipeline import run_rag_pipeline

from evaluation.benchmark import print_benchmark_results, run_benchmark
from evaluation.dataset import build_eval_dataset

def print_header(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def build_pipeline():
    docs = load_documents(config.FAQ_DIR, config.SUPPORT_DOCS_DIR, config.TICKETS_DIR)
    chunks = chunk_documents(docs, chunk_size=config.CHUNK_SIZE, overlap_ratio=config.CHUNK_OVERLAP_RATIO)
    vector_store = VectorStore.build(chunks)
    bm25_store = BM25Store.build(chunks)
    return docs, chunks, vector_store, bm25_store

def main():
    print_header("BUILD PIPELINE (Ingestion -> Chunking -> Indexing)")
    docs, chunks, vector_store, bm25_store = build_pipeline()
    print(f"Loaded {len(docs)} documents từ data/{{faq,support_docs,tickets}}/ -> {len(chunks)} chunks "
          f"(chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP_RATIO})")

    print_header("BENCHMARK — So sánh Experiment A/B/C ")
    eval_cases = build_eval_dataset(chunks)
    table = run_benchmark(eval_cases, vector_store, bm25_store, top_k=5)
    print_benchmark_results(table)
    print("\n(Số liệu OBSERVED trên bộ eval nhỏ minh họa — không đại diện thống kê "
          "cho 12.500 tài liệu thật. Chạy `python -m evaluation.benchmark` với eval "
          "set đầy đủ 100-300 case khi có dữ liệu thật.)")

    print_header("RUN PIPELINE - Experiment D (hybrid + rerank) trên câu hỏi thật")
    demo_queries = [
        "Error 500 khi submit ticket, có cách nào fix không?",
        "Làm sao để reset password cho user?",
    ]
    for q in demo_queries:
        result = run_rag_pipeline(
            query=q,
            vector_store=vector_store,
            bm25_store=bm25_store,
            method=config.DEFAULT_METHOD,
            access_level="internal",
            top_k=config.RETRIEVAL_TOP_K,
            rerank_top_n=3,
            context_word_budget=config.CONTEXT_WORD_BUDGET
        )
        print(f"\nQ: {q}")
        print(f"  Final context chunks : {result['final_chunk_ids']}")
        print(f"  Conflict detected (F4): {result['context_has_conflict']}")
        print(f"  Answer                : {result['answer']}")

if __name__ == "__main__":
    main()
