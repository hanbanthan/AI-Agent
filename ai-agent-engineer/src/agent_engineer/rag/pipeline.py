from agent_engineer.rag.base import Retriever
from agent_engineer.rag.document import RetrievedChunk
from agent_engineer.rag.errors import RetrievalError
from agent_engineer.rag.reranker import Reranker

class RAGPipeline:

    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker | None = None,
        rerank_candidates: int = 20,
    ) -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.rerank_candidates = rerank_candidates

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        try:
            candidate_k = (
                self.rerank_candidates
                if self.reranker is not None
                else top_k
            )

            results = self.retriever.retrieve(
                query,
                candidate_k,
            )

            if self.reranker is not None:
                results = self.reranker.rerank(
                    query,
                    results,
                    top_k,
                )
            else:
                results = results[:top_k]

            return results
        except RetrievalError as e:
            raise 
        except Exception as e:
            raise RetrievalError(
                f"Retrieval failed: {str(e)}"
            ) from e
    