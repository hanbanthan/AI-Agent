import pytest

from agent_engineer.agent import Agent, MaxStepsExceededError, StepType
from agent_engineer.llm import LLMResponse, MockLLM, ToolCall
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.tools.registry import ToolRegistry


def test_agent_returns_final_answer() -> None:
    llm = MockLLM(
        responses=[
            LLMResponse(
                content="An AI agent can make decisions and take actions.",
                model="mock-model",
            )
        ]
    )

    agent = Agent(llm=llm)

    result = agent.run("What is an AI agent?")

    assert result.answer == (
        "An AI agent can make decisions and take actions."
    )

    assert result.steps == 1
    assert len(result.trajectory) == 1
    assert result.trajectory.steps[0].step_type == StepType.FINAL

def test_agent_sends_user_message_to_llm() -> None:
    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Hello!",
                model="mock-model",
            )
        ]
    )

    agent = Agent(llm=llm)

    agent.run("Hello agent")

    assert len(llm.requests) == 1

    request = llm.requests[0]

    assert len(request.messages) == 1
    assert request.messages[0].role == "user"
    assert request.messages[0].content == "Hello agent"

def test_agent_stops_at_max_steps(search_tool) -> None:
    non_final_response = LLMResponse(
        content=None,
        model="mock-model",
        tool_calls=[
            ToolCall(
                id="call-1",
                name="search",
                arguments={"query": "Never finish"},
            )
        ],
    )

    llm = MockLLM(
        responses=[
            non_final_response,
            non_final_response,
            non_final_response,
        ]
    )

    registry = ToolRegistry()
    registry.register(search_tool)

    agent = Agent(
        llm=llm,
        tools=registry,
        max_steps=2,
    )

    with pytest.raises(MaxStepsExceededError):
        agent.run("Never finish")
