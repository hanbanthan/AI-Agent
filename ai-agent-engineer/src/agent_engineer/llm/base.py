from abc import ABC, abstractmethod

from .types import LLMRequest, LLMResponse

class LLM(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM based on the given request."""
        raise NotImplementedError
    