from agent_engineer.llm.base import LLM
from agent_engineer.llm.types import (
    LLMRequest,
    LLMResponse,
    Message,
)

def assert_provider_contract(
    llm: LLM,
) -> LLMResponse:

    request = LLMRequest(
        messages=[
            Message(
                role="user",
                content="Hello",
                tool_calls=[],
            )
        ]
    )

    response = llm.generate(
        request
    )

    assert isinstance(
        response,
        LLMResponse,
    )

    assert isinstance(
        response.model,
        str,
    )

    assert response.model

    assert (
        response.content is not None
        or response.tool_calls
    )

    assert (
        response.usage.input_tokens
        >= 0
    )

    assert (
        response.usage.output_tokens
        >= 0
    )

    assert (
        response.usage.total_tokens
        >= 0
    )

    assert (
        response.latency_ms
        is None
        or response.latency_ms >= 0
    )

    return response