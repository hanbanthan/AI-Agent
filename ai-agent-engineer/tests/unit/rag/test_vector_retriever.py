from agent_engineer.rag.vector_retriever import (
    VectorRetriever,
)

from agent_engineer.rag.document import Chunk


def test_empty_corpus(
    fake_embedding_model,
) -> None:

    retriever = VectorRetriever(
        chunks=[],
        embedding_model=fake_embedding_model,
    )

    assert retriever.retrieve("python") == []



def test_vector_exact_match(
    fake_embedding_model,
) -> None:

    chunks = [
        Chunk(
            id="1",
            document_id="doc1",
            text="python programming",
        ),
        Chunk(
            id="2",
            document_id="doc2",
            text="machine learning",
        ),
    ]

    retriever = VectorRetriever(
        chunks=chunks,
        embedding_model=fake_embedding_model,
    )

    results = retriever.retrieve(
        "python",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk.id == "1"

def test_top_k(
    fake_embedding_model,
) -> None:

    chunks = [
        Chunk(
            id=str(index),
            document_id=f"doc-{index}",
            text="python programming",
        )
        for index in range(10)
    ]

    retriever = VectorRetriever(
        chunks,
        fake_embedding_model,
    )

    results = retriever.retrieve(
        "python",
        top_k=3,
    )

    assert len(results) == 3