from agent_engineer.observability.trace import (
    Tracer,
)


class FakeClock:

    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(
        self,
        seconds: float,
    ) -> None:
        self.value += seconds


def test_span_duration() -> None:

    clock = FakeClock()

    tracer = Tracer(
        clock=clock
    )

    with tracer.trace("agent"):

        with tracer.span("llm") as span:
            clock.advance(0.25)

    assert span.duration_ms == 250.0