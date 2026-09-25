from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agent_engineer.observability.event import Event

class SpanStatus(str, Enum):
    RUNNING = "running"
    OK = "ok"
    ERROR = "error"

@dataclass
class Span:
    id: str
    trace_id: str
    name: str

    start_time: float

    parent_id: str | None = None
    end_time: float | None = None

    status: SpanStatus = SpanStatus.RUNNING

    attributes: dict[str, Any] = field(default_factory=dict)

    events: list[Event] = field(default_factory=list)

    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

    tool_calls: int = 0
    retries: int = 0

    error_type: str | None = None
    error_message: str | None = None

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None

        return (
            self.end_time - self.start_time
        ) * 1000

    @property
    def total_tokens(self) -> int:
        return (self.input_tokens + self.output_tokens)

    def add_event(
        self,
        event: Event,
    ) -> None:
        self.events.append(event
    )

    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        cost: float = 0.0,
    ) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cost += cost

    def record_tool_call(self) -> None:
        self.tool_calls += 1

    def record_retry(self) -> None:
        self.retries += 1

    def finish(
        self,
        end_time: float,
        error: Exception | None = None,
    ) -> None:

        self.end_time = end_time

        if error is None:
            self.status = SpanStatus.OK
            return

        self.status = SpanStatus.ERROR
        self.error_type = type(error).__name__
        self.error_message = str(error)
