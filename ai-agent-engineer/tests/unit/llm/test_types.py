from agent_engineer.llm import (
    LLMRequest,
    LLMResponse,
    Message,
    ToolCall,
    Usage,
)

def test_message() -> None:
    message = Message(
        role="user",
        content="Hello",
    )

    assert message.role == "user"
    assert message.content == "Hello"

def test_usage_total_tokens() -> None:
    usage = Usage(
        input_tokens=100,
        output_tokens=50,
    )

    assert usage.total_tokens == 150

def test_llm_request() -> None:
    request = LLMRequest(
        messages=[
            Message(
                role="user",
                content="What is an AI agent?",
            )
        ],
        temperature=0.2,
    )

    assert len(request.messages) == 1
    assert request.messages[0].role == "user"
    assert request.temperature == 0.2
    assert request.tools == []


def test_tool_call() -> None:
    tool_call = ToolCall(
        id="call_123",
        name="search",
        arguments={"query": "AI agents"},
    )

    assert tool_call.id == "call_123"
    assert tool_call.name == "search"
    assert tool_call.arguments["query"] == "AI agents"


def test_llm_response_usage() -> None:
    response = LLMResponse(
        content="An AI agent can use tools.",
        model="mock-model",
        usage=Usage(
            input_tokens=20,
            output_tokens=10,
        ),
    )

    assert response.content == "An AI agent can use tools."
    assert response.model == "mock-model"
    assert response.usage.total_tokens == 30
    assert response.tool_calls == []