import time
import uuid

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from collections.abc import Callable, Generator

from agent_engineer.observability.span import Span

Clock = Callable[[], float]

@dataclass
class Trace:
    id: str
    name: str
    start_time: float

    end_time: float | None = None

    spans: list[Span] = field(default_factory=list)

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None

        return (self.end_time - self.start_time) * 1000

    def add_span(
        self,
        span: Span,
    ) -> None:
        self.spans.append(span)

class Tracer:

    def __init__(
        self,
        clock: Clock = time.perf_counter
    ) -> None:
        self.clock = clock

        self._current_trace: ContextVar[Trace | None] = ContextVar(
            "current_trace",
            default=None
        )

        self._current_span: ContextVar[Span | None] = ContextVar(
            "current_span",
            default=None
        )

    @property
    def current_trace(self) -> Trace | None:
        return self._current_trace.get()

    @property
    def current_span(self) -> Span | None:
        return self._current_span.get()

    @contextmanager
    def trace(
        self,
        name: str,
    ) -> Generator[Trace, None, None]:

        trace = Trace(
            id=str(uuid.uuid4()),
            name=name,
            start_time=self.clock()
        )

        trace_token = (
            self._current_trace.set(trace)
        )

        span_token = (
            self._current_span.set(None)    
        )

        try:
            yield trace

        finally:
            trace.end_time = self.clock()

            self._current_trace.reset(trace_token)
            self._current_span.reset(span_token)

    @contextmanager
    def span(
        self,
        name: str,
    ) -> Generator[Span, None, None]:

        trace = self.current_trace

        if trace is None:
            raise RuntimeError(
                "No active trace. "
                "Spans can only be created within a trace context."
            )

        parent = self.current_span

        span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace.id,
            name=name,
            parent_id=(
                parent.id
                if parent is not None
                else None
            ),
            start_time=self.clock(),
        )

        trace.add_span(span)

        token = self._current_span.set(span)

        try: 
            yield span

        except Exception as e:
            span.finish(
                end_time=self.clock(),
                error=e,
            )
            raise

        else:
            span.finish(
                end_time=self.clock(),
            )

        finally:
            self._current_span.reset(token)