class LLMError(Exception):
    """Base class for all LLM-related errors."""
    retryable: bool = False

class LLMTimeoutError(LLMError):
    """Raised when a request to the LLM times out."""
    retryable: bool = True

class LLMRateLimitError(LLMError):
    """Raised when the LLM request exceeds the rate limit."""
    retryable: bool = True

class LLMAuthenticationError(LLMError):
    """Raised when there is an authentication error with the LLM service."""
    retryable: bool = False

class LLMInvalidResponseError(LLMError):
    """Raised when the LLM returns an invalid or unexpected response."""
    retryable: bool = False