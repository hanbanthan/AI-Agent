from abc import ABC, abstractmethod
from dataclasses import dataclass

class BackoffStrategy(ABC):

    @abstractmethod
    def get_delay(
        self,
        retry_number: int,
    ) -> float:
        raise NotImplementedError

@dataclass(frozen=True)
class ExponentialBackoff(BackoffStrategy):
    initial_delay: float = 0.1
    multiplier: float = 2.0
    max_delay: float = 5.0

    def get_delay(
        self,
        retry_number: int,
    ) -> float:

        if retry_number < 0:
            raise ValueError("retry_number must be a non-negative integer.")

        delay = (
            self.initial_delay * (self.multiplier ** retry_number)
        )
        return min(delay, self.max_delay)

    