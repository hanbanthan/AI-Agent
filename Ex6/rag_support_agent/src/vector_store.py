"""
vector_store.py - lưu trữ vector + tìm kiếm theo cosine similarity 
(Experiment A trong bài 6)

Tách khỏi embeddings.py có chủ đích: đây là 2 hệ thống khác nhau 
trong thực tế (embedding.model vs Vector DB như Pinecone/Weaviate/pgvector) -
bạn có thể đổi 1 trong 2 mà không đụng cái còn lại. Ở demo này, 
VectorStore giữ ma trận trong RAM; production nên thay bằng client của
1 Vector DB thật.
"""

from dataclasses import dataclass

from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import EmbeddingModel
from .models import Chunk, RetrievalResult

@dataclass
class VectorStore:
    embedding_model: EmbeddingModel
    matrix: any                       # ma trận vector của toàn bộ chunk, shape (n_chunks, n_dims)
    chunks: list[Chunk]

    @classmethod
    def build(cls, chunks: list[Chunk], embedding_model: EmbeddingModel | None = None) -> "VectorStore":
        embedding_model = embedding_model or EmbeddingModel()
        matrix = embedding_model.fit_transform([c.text for c in chunks])
        return cls(embedding_model=embedding_model, matrix=matrix, chunks=chunks)

    def search(self, query: str, top_k: int = 25) -> list[RetrievalResult]:
        q_vec = self.embedding_model.transform_query(query)
        sims = cosine_similarity(q_vec, self.matrix)[0]
        ranked_idx = sims.argsort()[::-1][:top_k]
        return [
            RetrievalResult(chunk=self.chunks[i], score=float(sims[i]), method="vector")
            for i in ranked_idx
            if sims[i] > 0
        ]
    
