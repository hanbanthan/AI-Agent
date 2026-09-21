import math

from agent_engineer.rag.base import Retriever
from agent_engineer.rag.document import (
    Chunk,
    RetrievedChunk,
)
from agent_engineer.rag.embeddings import EmbeddingModel

def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:

    if len(a) != len(b):
        raise ValueError("Vectors must be of the same length")

    dot_product = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)

class VectorRetriever(Retriever):

    def __init__(
        self,
        chunks: list[Chunk],
        embedding_model: EmbeddingModel,
    ) -> None:
        self.chunks = chunks
        self.embedding_model = embedding_model

        self._embeddings = embedding_model.embed_many(
            [
                chunk.text
                for chunk in chunks
            ]
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        if top_k <= 0:
            return []

        if not self.chunks:
            return []

        query_embedding = self.embedding_model.embed(
            query
        )

        results = [
            RetrievedChunk(
                chunk=chunk,
                score=cosine_similarity(
                    query_embedding,
                    embedding,
                ),
            )
            for chunk, embedding in zip(
                self.chunks,
                self._embeddings,
            )
        ]

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]


        