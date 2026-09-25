"""
embeddings.py - biến text thành vector số.

STAND-IN quan trọng: sandbox này không có mạng ra ngoài để tải embedding
model thật (OpenAI/Voyage/Cohere/self-host sentence-transformers). Class 
`EmbeddingModel` dưới đây dùng TF-IDF (scikit-learn) làm thay thế - vẫn
đúng cấu trúc "vector + cosin similarity" của semantic vector search,
nhưng là lexical (dựa tần suất từ), không bắt được đồng nghĩa/diễn giải 
khác nhau như embedding model thật.

Đây là điểm duy nhất cần sửa khi lên production - mọi module khác 
(vector_store.py, hybrid_search.py, rag_pipeline.py) chỉ gọi qua
interface `fit_transform()` / `transform_query()`, không cần 
biết bên dưới là TF-IDF hay embedding API thật.
"""

from sklearn.feature_extraction.text import TfidfVectorizer

class EmbeddingModel:
    """Interface chung - thay bằng embedding API thật khi lên production:

    class EmbeddingModel:
        def fit_transform(self, texts):
            return openai_client.embeddings.create(input=texts, model="text-embedding-3-small")
        def transform_query(self, query):
            return openai_client.embeddings.create(input=[query], model="text-embedding-3-small")
    """

    def __init__(self):
        self._vectorizer = TfidfVectorizer()
        self.__fitted = False

    def fit_transform(self, texts: list[str]):
        matrix = self._vectorizer.fit_transform(texts)
        self.__fitted = True
        return matrix

    def transform_query(self, query: str):
        if not self.__fitted:
            raise RuntimeError("EmbeddingModel chưa fit_transform() trước khi transform_query()")
        return self._vectorizer.transform([query])