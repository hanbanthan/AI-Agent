from agent_engineer.llm.types import Message, LLMRequest, LLMResponse
from agent_engineer.optimization.router import (
    ModelRouter,
    RouteRule,
)

from agent_engineer.llm.mock import MockLLM
from agent_engineer.llm.errors import LLMTimeoutError

def test_router_rule() -> None:

    small = MockLLM(
        responses=[
            LLMResponse(
                content="small",
                model="small",
            )
        ]
    )

    large = MockLLM(
        responses=[
            LLMResponse(
                content="large",
                model="large",
            )
        ]   
    )

    router = ModelRouter(
        default=large,
        rules=[
            RouteRule(
                name="short-input",
                predicate=lambda request: (
                    len(
                        request.messages[-1].content
                    )
                    <50
                ),
                llm=small,
            )
        ],
    )

    response = router.generate(
        LLMRequest(
            messages=[
                Message(
                    role="user",
                    content="Hello",
                    tool_calls=[],
                )
            ]
        )
    )

    assert response.content == "small"

def test_fallback_model() -> None:

    primary = MockLLM(
        responses=[
            LLMTimeoutError(
                "timeout"
            )
        ]
    )

    fallback = MockLLM(
        responses=[
            LLMResponse(
                content="fallback answer",
                model="fallback",
            )
        ]
    )

    router = ModelRouter(
        default=primary,
        fallback=fallback,
    )

    response = router.generate(
        LLMRequest(
            messages=[
                Message(
                    role="user",
                    content="Hello",
                    tool_calls=[],
                )
            ]
        )       
    )

    assert response.content == "fallback answer"