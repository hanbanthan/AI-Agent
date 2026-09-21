from agent_engineer.rag.base import Retriever
from agent_engineer.rag.document import Chunk, RetrievedChunk

def normalize(
    results: list[RetrievedChunk],
) -> dict[str, float]:
    if not results:
        return {}

    scores = [
        result.score
        for result in results
    ]

    minimum = min(scores)
    maximum = max(scores)

    if minimum == maximum:
        return {
            result.chunk.id: 1.0
            for result in results
        }

    return {
        result.chunk.id: (result.score - minimum) / (maximum - minimum)
        for result in results
    }

class HybridRetriever(Retriever):

    def __init__(
        self,
        vector_retriever: Retriever,
        bm25_retriever: Retriever,
        alpha: float = 0.5,
    ) -> None:

        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")

        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.alpha = alpha

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        candidate_k = max(
            top_k * 2,
            top_k,
        )

        vector_results = (
            self.vector_retriever.retrieve(
                query,
                candidate_k,
            )
        )

        bm25_results = (
            self.bm25_retriever.retrieve(
                query,
                candidate_k,
            )
        )

        vector_scores = normalize(vector_results)
        bm25_scores = normalize(bm25_results)

        chunks = {}

        for result in (
            vector_results
            + bm25_results
        ):
            chunks[result.chunk.id] = result.chunk

        results = []

        for chunk_id, chunk in chunks.items():
            vector_score = vector_scores.get(chunk_id, 0.0)
            bm25_score = bm25_scores.get(chunk_id, 0.0)

            bm25_score = bm25_scores.get(
                chunk_id,
                0.0,
            )

            hybrid_score = (
                self.alpha * vector_score
                + (1 - self.alpha) * bm25_score
            )

            results.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=hybrid_score,
                )
            )   

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]
    
        

