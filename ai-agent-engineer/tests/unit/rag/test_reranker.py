from agent_engineer.rag.document import (
    Chunk,
    RetrievedChunk,
)

from agent_engineer.rag.reranker import (
    KeywordReranker,
)

def test_reranker_changes_order() -> None:
    results = [
        RetrievedChunk(
            chunk=Chunk(
                id="1",
                document_id="a",
                text="completely unrelated text",
            ),
            score=0.9,
        ),
        RetrievedChunk(
            chunk=Chunk(
                id="2",
                document_id="b",
                text="python agent tool",
            ),
            score=0.5,
        ),
    ]
     
    reranker = KeywordReranker()

    reranked = reranker.rerank(
        query="python agent",
        results=results,
        top_k=2,
    )

    assert reranked[0].chunk.id == "2"
    