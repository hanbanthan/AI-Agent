from agent_engineer.errors import AgentError

class MemorySystemError(AgentError):
    """Base class for memory system errors."""
    retryable: bool = False

class MemoryNotFoundError(MemorySystemError):
    """Raised when a requested memory item is not found."""
    retryable: bool = False

class DuplicateMemoryError(MemorySystemError):
    """Raised when attempting to add a duplicate memory item."""
    retryable: bool = False

class MemoryRetrievalError(MemorySystemError):
    """Raised when there is an error retrieving memory."""
    retryable: bool = True

