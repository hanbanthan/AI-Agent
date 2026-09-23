from collections.abc import Iterable

from agent_engineer.llm.base import LLM
from agent_engineer.llm.errors import (
    LLMInvalidResponseError,
)
from agent_engineer.llm.types import (
    LLMRequest,
    LLMResponse,
)


class MockLLM(LLM):
    def __init__(
        self, 
        responses: Iterable[
            LLMResponse | Exception
            ],
    ) -> None:
        self._responses = iter(responses)
        self.requests: list[LLMRequest] = []

    def generate(
        self, 
        request: LLMRequest
    ) -> LLMResponse:

        self.requests.append(request)

        try:
            result = next(self._responses)
        except StopIteration as exc:
            raise LLMInvalidResponseError("no responses remaining") from exc

        if isinstance(result, Exception):
            raise result

        return result
    