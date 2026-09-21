from agent_engineer.rag.bm25_retriever import (
    BM25Retriever,
)
from agent_engineer.rag.document import Chunk

def test_bm25_exact_match() -> None:
    chunks = [
        Chunk(
            id="1",
            document_id="a",
            text="python agent framework",
        ),
        Chunk(
            id="2",
            document_id="b",
            text="cooking rice recipe",
        ),
    ]

    retriever = BM25Retriever(chunks)

    results = retriever.retrieve(
        "python agent",
        top_k=1,
    )

    assert results[0].chunk.id == "1"