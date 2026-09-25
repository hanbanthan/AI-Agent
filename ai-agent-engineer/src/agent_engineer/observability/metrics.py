from dataclasses import dataclass

from agent_engineer.observability.trace import Trace

from agent_engineer.observability.span import SpanStatus

@dataclass(frozen=True)
class TraceMetrics:
    latency_ms: float

    input_tokens: int
    output_tokens: int
    total_tokens: int

    cost: float

    tool_calls: int
    retries: int

    span_count: int
    error_count: int

def aggregate_trace(
    trace: Trace,
) -> TraceMetrics:

    return TraceMetrics(
        latency_ms=trace.duration_ms or 0.0,
        input_tokens=sum(span.input_tokens for span in trace.spans),
        output_tokens=sum(span.output_tokens for span in trace.spans),
        total_tokens=sum(span.total_tokens for span in trace.spans),
        cost=sum(span.cost for span in trace.spans),
        tool_calls=sum(span.tool_calls for span in trace.spans),
        retries=sum(span.retries for span in trace.spans),
        span_count=len(trace.spans),
        error_count=sum(1 for span in trace.spans if span.status == SpanStatus.ERROR
        ),
    )

