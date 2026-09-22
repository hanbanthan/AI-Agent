from agent_engineer.errors import AgentError

class PlanningError(AgentError):
    """Base exception for planning-related errors."""
    retryable: bool = False
    