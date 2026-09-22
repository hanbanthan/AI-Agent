class AgentError(Exception):
    """Base class for all exceptions raised by the Agent Engineer."""

    retryable: bool = False
    