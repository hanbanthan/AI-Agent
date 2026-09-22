from agent_engineer.errors import AgentError

class RAGError(AgentError):
    """Base class for RAG-related errors."""
    retryable: bool = False

class RetrievalError(RAGError):
    """Raised when there is an error during the retrieval process."""
    retryable: bool = False

class RetrievalUnavailableError(RAGError):
    """Raised when the retrieval service is unavailable."""
    retryable: bool = True