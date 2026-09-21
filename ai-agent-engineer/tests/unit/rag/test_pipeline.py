import pytest

from agent_engineer.rag.base import Retriever
from agent_engineer.rag.errors import RetrievalError
from agent_engineer.rag.pipeline import RAGPipeline
class BrokenRetriever(Retriever):
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5
    ):
        raise RuntimeError("Vector database is unavailable")

def test_retrieval_failure_is_normalized() -> None:
    pipeline = RAGPipeline(
        retriever=BrokenRetriever(),
    )

    with pytest.raises(
        RetrievalError,
        match="Retrieval failed: Vector database is unavailable",
    ):
        pipeline.retrieve(
            query="python"
        )
