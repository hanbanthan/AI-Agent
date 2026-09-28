import pytest

from agent_engineer.llm import (
    LLMRequest,
    LLMResponse,
    Message,
    MockLLM,
    Usage,
)

from agent_engineer.llm.errors import LLMInvalidResponseError


def make_request(content: str = "Hello") -> LLMRequest:
    return LLMRequest(
        messages=[
            Message(
                role="user",
                content=content,
                tool_calls=[],
            )
        ]
    )

def test_mock_llm_returns_response() -> None:
    expected = LLMResponse(
        content="Hi!",
        model="mock-model",
        usage=Usage(
            input_tokens=1,
            output_tokens=1,
        ),
    )

    llm = MockLLM([expected])

    response = llm.generate(make_request())

    assert response == expected


def test_mock_llm_returns_responses_in_order() -> None:
    response_1 = LLMResponse(
        content="First",
        model="mock-model",
    )

    response_2 = LLMResponse(
        content="Second",
        model="mock-model",
    )

    llm = MockLLM([
        response_1,
        response_2,
    ])

    assert llm.generate(make_request()).content == "First"
    assert llm.generate(make_request()).content == "Second"


def test_mock_llm_records_requests() -> None:
    llm = MockLLM([
        LLMResponse(
            content="Hi",
            model="mock-model",
        )
    ])

    request = make_request("Hello AI")

    llm.generate(request)

    assert len(llm.requests) == 1
    assert llm.requests[0] == request
    assert llm.requests[0].messages[0].content == "Hello AI"


def test_mock_llm_raises_when_responses_exhausted() -> None:
    llm = MockLLM([
        LLMResponse(
            content="Only response",
            model="mock-model",
        )
    ])

    llm.generate(make_request())

    with pytest.raises(
        LLMInvalidResponseError,
        match="no responses remaining",
    ):
        llm.generate(make_request())