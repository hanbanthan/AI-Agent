import pytest

from agent_engineer.rag.embeddings import EmbeddingModel

from agent_engineer.rag.document import Chunk
from agent_engineer.rag.hybrid_retriever import HybridRetriever
from agent_engineer.rag.vector_retriever import VectorRetriever
from agent_engineer.rag.bm25_retriever import BM25Retriever

class FakeEmbeddingModel(EmbeddingModel):

    def __init__(
        self,
        embeddings: dict[str, list[float]],
    ) -> None:
        self.embeddings = embeddings

    def embed(
        self,
        text: str,
    ) -> list[float]:

        return self.embeddings.get(
            text,
            [0.0, 0.0],
        )


@pytest.fixture
def fake_embedding_model() -> FakeEmbeddingModel:
    return FakeEmbeddingModel(
        {
            "python programming": [1.0, 0.0],
            "machine learning": [0.0, 1.0],
            "python": [1.0, 0.0],
        }
    )

@pytest.fixture
def hybrid_retriever(
    fake_embedding_model,
) -> HybridRetriever:
    chunks = [
        Chunk(
            id="1",
            document_id="doc-1",
            text="python programming",
        ),
        Chunk(
            id="2",
            document_id="doc-2",
            text="machine learning",
        ),
        Chunk(
            id="3",
            document_id="doc-3",
            text="python agent",
        ),
    ]

    vector_retriever = VectorRetriever(
        chunks=chunks,
        embedding_model=fake_embedding_model,
    )

    bm25_retriever = BM25Retriever(
        chunks=chunks,
    )

    return HybridRetriever(
        vector_retriever=vector_retriever,
        bm25_retriever=bm25_retriever,
        alpha=0.5,
    )