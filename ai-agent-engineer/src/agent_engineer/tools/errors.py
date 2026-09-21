class ToolError(Exception):
    """Base exception for tool-related errors."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class DuplicateToolError(ToolError):
    """Raised when a tool with the same name is already registered."""


class ToolValidationError(ToolError):
    """Raised when tool arguments are invalid."""


class ToolExecutionError(ToolError):
    """Raised when a tool fails during execution."""