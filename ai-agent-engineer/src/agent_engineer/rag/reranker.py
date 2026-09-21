from abc import ABC, abstractmethod

from agent_engineer.rag.bm25_retriever import tokenize
from agent_engineer.rag.document import RetrievedChunk

class Reranker(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        raise NotImplementedError

class KeywordReranker(Reranker):

    def rerank(
        self,
        query: str,
        results: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:

        query_terms = set(tokenize(query))

        reranked = []

        for result in results:
            document_terms = set(
                tokenize(result.chunk.text)
            )

            overlap = len(
                query_terms & document_terms
            )

            reranked.append(
                RetrievedChunk(
                    chunk=result.chunk,
                    score=float(overlap),
                )
            )

        reranked.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return reranked[:top_k]
    
