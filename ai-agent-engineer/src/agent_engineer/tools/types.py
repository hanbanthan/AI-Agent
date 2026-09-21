from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ToolParameter:
    name: str
    type: type
    description: str
    required: bool = True

@dataclass(frozen=True)
class ToolSchema:
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str | None = None

@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    success: bool
    output: Any | None = None
    error: str | None = None
    call_id: str | None = None