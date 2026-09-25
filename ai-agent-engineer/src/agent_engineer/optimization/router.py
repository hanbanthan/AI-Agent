from dataclasses import dataclass
from collections.abc import Callable

from agent_engineer.errors import AgentError
from agent_engineer.llm.base import LLM
from agent_engineer.llm.types import (
    LLMRequest,
    LLMResponse,
)

@dataclass(frozen=True)
class RouteRule:
    name: str
    predicate: Callable[
        [LLMRequest],
        bool,
    ]
    llm: LLM

class ModelRouter(LLM):

    def __init__(
        self,
        default: LLM,
        rules: list[RouteRule] | None = None,
        fallback: LLM | None = None,
    ) -> None:
        self.default = default
        self.rules = rules or []
        self.fallback = fallback

    def select(
        self,
        request: LLMRequest,
    ) -> LLM:

        for rule in self.rules:
            if rule.predicate(request):
                return rule.llm

        return self.default

    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        selected = self.select(request)

        try:
            return selected.generate(request)
        except AgentError as exc:

            if (
                self.fallback is None
                or not exc.retryable
                or selected is self.fallback
            ): raise

            return self.fallback.generate(request)

