import pytest

from typing import Any

from agent_engineer.tools.errors import (
    ToolExecutionError,
    ToolValidationError,
)
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.tools.registry import ToolRegistry
from agent_engineer.tools.types import ToolCall

from agent_engineer.tools.base import Tool
from agent_engineer.tools.types import ToolSchema

from agent_engineer.agent import Agent
from agent_engineer.llm import LLMResponse, MockLLM, ToolCall

def create_executor(search_tool) -> ToolExecutor:
    registry = ToolRegistry()
    registry.register(search_tool)
    return ToolExecutor(registry=registry)

def test_valid_arguments(search_tool) -> None:
    executor = create_executor(search_tool)

    result = executor.execute(
        ToolCall(
            name="search",
            arguments={"query": "AI agents"},
        )
    )

    assert result.success is True

def test_missing_argument(search_tool) -> None:
    executor = create_executor(search_tool)

    with pytest.raises(ToolValidationError):
        executor.execute(
            ToolCall(
                name="search",
                arguments={},
            )
        )


def test_invalid_argument_type(search_tool) -> None:
    executor = create_executor(search_tool)

    with pytest.raises(ToolValidationError):
        executor.execute(
            ToolCall(
                name="search",
                arguments={"query": 123},
            )
        )


def test_unknown_argument(search_tool) -> None:
    executor = create_executor(search_tool)

    with pytest.raises(ToolValidationError):
        executor.execute(
            ToolCall(
                name="search",
                arguments={
                    "query": "AI",
                    "limit": 10,
                },
            )
        )

def test_tool_execution_success(search_tool) -> None:
    executor = create_executor(search_tool)

    result = executor.execute(
        ToolCall(
            name="search",
            arguments={"query": "AI agents"},
        )
    )

    assert result.success is True
    assert result.tool_name == "search"
    #assert result.output == "Result for: AI agents"

class FailingTool(Tool):

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="failing",
            description="Always fails.",
        )

    def execute(self, **kwargs: Any) -> Any:
        raise RuntimeError("Something went wrong")


def test_tool_execution_failure() -> None:
    registry = ToolRegistry()
    registry.register(FailingTool())

    executor = ToolExecutor(registry)

    with pytest.raises(
        ToolExecutionError,
        match="Something went wrong",
    ):
        executor.execute(
            ToolCall(
                name="failing",
                arguments={},
            )
        )

def test_tool_observation_is_sent_back_to_llm(
    search_tool,
) -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock-model",
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="search",
                        arguments={
                            "query": "AI agents",
                        },
                    )
                ],
            ),
            LLMResponse(
                content="Final answer",
                model="mock-model",
            ),
        ]
    )

    registry = ToolRegistry()
    registry.register(search_tool)

    executor = ToolExecutor(registry)

    agent = Agent(
        llm=llm,
        tools=registry,
    )

    agent.run("Research AI agents")

    assert len(llm.requests) == 2

    second_request = llm.requests[1]

    tool_messages = [
        message
        for message in second_request.messages
        if message.role == "tool"
    ]

    assert len(tool_messages) == 1

    assert (
        tool_messages[0].content
        == "Result for: AI agents"
    )

    assert tool_messages[0].tool_call_id == "call-1"