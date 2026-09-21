class LLMError(Exception):
    """Base class for all LLM-related errors."""

class LLMTimeoutError(LLMError):
    """Raised when a request to the LLM times out."""

class LLMRateLimitError(LLMError):
    """Raised when the LLM request exceeds the rate limit."""

class LLMAuthenticationError(LLMError):
    """Raised when there is an authentication error with the LLM service."""

class LLMInvalidResponseError(LLMError):
    """Raised when the LLM returns an invalid or unexpected response."""
