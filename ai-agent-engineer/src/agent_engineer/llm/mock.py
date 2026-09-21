from collections.abc import Iterable

from .base import LLM
from .errors import LLMInvalidResponseError
from .types import LLMRequest, LLMResponse

class MockLLM(LLM):
    def __init__(self, responses: Iterable[LLMResponse]) -> None:
        self._responses = iter(responses)
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)

        try:
            return next(self._responses)
        except StopIteration as exc:
            raise LLMInvalidResponseError("no responses remaining") from exc