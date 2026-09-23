import pytest

from agent_engineer.llm.errors import (
    LLMTimeoutError,
    LLMRateLimitError,
    LLMInvalidResponseError,
)
from agent_engineer.resilience.retry import (
    RetryExecutor,
    RetryPolicy,
)


def test_retry_success() -> None:

    calls = 0

    def operation() -> str:
        nonlocal calls

        calls += 1

        if calls < 3:
            raise LLMTimeoutError(
                "Timed out"
            )

        return "success"

    executor = RetryExecutor(
        policy=RetryPolicy(
            max_retries=2
        ),
        sleeper=lambda _: None,
    )

    result = executor.execute(operation)

    assert result == "success"
    assert calls == 3


def test_rate_limit_is_retryable() -> None:
    error = LLMRateLimitError(
        "Too many requests"
    )

    assert error.retryable is True


def test_retry_exhausted() -> None:
    calls = 0

    def operation() -> None:
        nonlocal calls

        calls += 1

        raise LLMTimeoutError(
            "Still unavailable"
        )

    executor = RetryExecutor(
        policy=RetryPolicy(
            max_retries=2
        ),
        sleeper=lambda _: None,
    )

    with pytest.raises(
        LLMTimeoutError
    ):
        executor.execute(operation)

    assert calls == 3


def test_non_retryable_error_is_not_retried() -> None:
    calls = 0

    def operation() -> None:
        nonlocal calls

        calls += 1

        raise LLMInvalidResponseError(
            "Malformed response"
        )

    executor = RetryExecutor(
        policy=RetryPolicy(
            max_retries=10
        ),
        sleeper=lambda _: None,
    )

    with pytest.raises(
        LLMInvalidResponseError
    ):
        executor.execute(operation)

    assert calls == 1