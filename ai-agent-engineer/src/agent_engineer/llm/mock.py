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

    from collections.abc import Iterable

from agent_engineer.llm.base import LLM
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

        self._responses = iter(
            responses
        )

        self.requests: list[
            LLMRequest
        ] = []

    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        self.requests.append(
            request
        )

        response = next(
            self._responses
        )

        if isinstance(
            response,
            Exception,
        ):
            raise response

        return response
    