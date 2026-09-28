from dataclasses import dataclass, field
from typing import Any, Literal
from agent_engineer.tools.types import ToolCall

Role = Literal["system", "user", "assistant", "tool"]

@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    tool_calls: list[ToolCall]
    tool_call_id: str | None = None
    name: str | None = None

@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

@dataclass(frozen=True)
class StructuredOutput:
    name: str
    schema: dict[str, Any]
    strict: bool = True

@dataclass(frozen=True)
class LLMRequest:
    messages: list[Message]
    temperature: float = 0.0
    max_tokens: int | None = None
    tools: list[dict[str, Any]] = field(default_factory=list)
    structured_output: StructuredOutput | None = None

@dataclass(frozen=True)
class LLMResponse:
    content: str | None
    model: str
    usage: Usage = field(default_factory=Usage)
    tool_calls: list[ToolCall] = field(default_factory=list)
    latency_ms: float = 0.0
    raw_response: Any = None

    @property
    def is_final(self) -> bool:
        return len(self.tool_calls) == 0
    
