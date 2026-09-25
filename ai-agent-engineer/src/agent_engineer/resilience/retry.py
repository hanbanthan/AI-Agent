import time

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

from agent_engineer.errors import AgentError
from agent_engineer.resilience.backoff import (
    BackoffStrategy,
    ExponentialBackoff,
)

T = TypeVar("T")

@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2

    backoff: BackoffStrategy = field(default_factory=ExponentialBackoff)

    def __post_init__(self):
        if self.max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer.")

    def should_retry(
        self,
        error: AgentError,
        retries_done: int,
    ) -> bool:

        return (
            error.retryable and retries_done < self.max_retries
        )

class RetryExecutor:
    def __init__(
        self,
        policy: RetryPolicy,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        
        self.policy = policy
        self.sleeper = sleeper

    def execute(
        self,
        operation: Callable[[], T],
        on_retry: (
            Callable[[AgentError, int], None]
            | None
        ) = None,
    ) -> T:

        retries_done = 0

        while True:
            try:
                return operation()
            except AgentError as error:
                if not self.policy.should_retry(error, retries_done):
                    raise

                delay = self.policy.backoff.get_delay(retries_done)
                self.sleeper(delay)
                retries_done += 1

                if on_retry is not None:
                    on_retry(error, retries_done, delay)

                self.sleeper(delay)