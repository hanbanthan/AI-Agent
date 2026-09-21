
def test_hybrid_deduplicates_chunk_ids(
        hybrid_retriever,
) -> None:
    results = hybrid_retriever.retrieve(
        query="python",
        top_k=10,
    )

    ids = [
        result.chunk.id
        for result in results
    ]

    assert len(ids) == len(set(ids))

def test_hybrid_score_is_normalized(
        hybrid_retriever,
) -> None:
    results = hybrid_retriever.retrieve(
        query="python",
        top_k=5,
    )

    for result in results:
        assert 0.0 <= result.score <= 1.0