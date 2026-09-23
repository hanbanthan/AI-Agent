from agent_engineer.resilience.backoff import (
    ExponentialBackoff,
)


def test_exponential_backoff() -> None:

    backoff = ExponentialBackoff(
        initial_delay=1.0,
        multiplier=2.0,
        max_delay=5.0,
    )

    assert backoff.get_delay(0) == 1.0
    assert backoff.get_delay(1) == 2.0
    assert backoff.get_delay(2) == 4.0

    # capped
    assert backoff.get_delay(3) == 5.0
    assert backoff.get_delay(10) == 5.0