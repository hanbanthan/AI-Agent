from agent_engineer.errors import AgentError

class AgentError(AgentError):
    """Base class for all agent-related errors."""
    retryable: bool = False

class MaxStepsExceededError(AgentError):
    """Raised when the agent exceeds the maximum number of allowed steps."""

class RepeatedActionError(AgentError):
    """Raised when the agent detects a repetition in its actions or thoughts."""