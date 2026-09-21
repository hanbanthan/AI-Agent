class RAGError(Exception):
    """Base class for RAG-related errors."""

class RetrievalError(RAGError):
    """Raised when there is an error during the retrieval process."""