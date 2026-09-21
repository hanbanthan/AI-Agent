class AgentError(Exception):
    """Base class for all agent-related errors."""

class MaxStepsExceededError(AgentError):
    """Raised when the agent exceeds the maximum number of allowed steps."""
