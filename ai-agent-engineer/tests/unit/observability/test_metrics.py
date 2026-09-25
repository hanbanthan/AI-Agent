from agent_engineer.observability.metrics import (
    aggregate_trace,
)

from agent_engineer.observability.trace import (
    Trace,
    Tracer,
)

def test_token_and_cost_aggregation() -> None:

    tracer = Tracer()

    with tracer.trace("agent") as trace:

        with tracer.span("llm-1") as first:
            first.add_usage(
                input_tokens=100,
                output_tokens=20,
                cost=0.01,
            )

        with tracer.span("llm-2") as second:
            second.add_usage(
                input_tokens=50,
                output_tokens=10,
                cost=0.005,
            )

    metrics = aggregate_trace(trace)

    assert metrics.input_tokens == 150
    assert metrics.output_tokens == 30
    assert metrics.total_tokens == 180
    assert metrics.cost == 0.015