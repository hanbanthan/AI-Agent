from agent_engineer.errors import AgentError

class ToolError(AgentError):
    """Base exception for tool-related errors."""
    retryable: bool = False


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""
    retryable: bool = False


class DuplicateToolError(ToolError):
    """Raised when a tool with the same name is already registered."""
    retryable: bool = False

class ToolValidationError(ToolError):
    """Raised when tool arguments are invalid."""
    retryable: bool = False


class ToolValidationError(ToolError):
    """Raised when tool arguments are invalid."""
    retryable: bool = False


class ToolExecutionError(ToolError):
    """Raised when a tool fails during execution."""
    retryable: bool = False