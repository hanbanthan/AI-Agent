import pytest

from agent_engineer.agent.agent import Agent
from agent_engineer.agent.errors import (
    RepeatedActionError,
)
from agent_engineer.agent.loop_guard import (
    LoopPolicy,
)

from agent_engineer.llm.errors import (
    LLMTimeoutError,
)
from agent_engineer.llm.mock import MockLLM
from agent_engineer.llm.types import (
    LLMResponse,
    Usage,
)

from agent_engineer.resilience.backoff import (
    ExponentialBackoff,
)
from agent_engineer.resilience.retry import (
    RetryPolicy,
)

from agent_engineer.tools.errors import (
    ToolExecutionError,
)
from agent_engineer.tools.registry import (
    ToolRegistry,
)
from agent_engineer.tools.types import (
    ToolCall,
)

from tests.integration.helpers import (
    AddTool,
    FailingTool,
)

def usage() -> Usage:
    return Usage(
        input_tokens=10,
        output_tokens=5,
    )

def test_tool_failure_is_propagated_or_handled() -> None:

    tools = ToolRegistry()

    tools.register(
        FailingTool()
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock",
                usage=usage(),
                tool_calls=[
                    ToolCall(
                        id="fail-1",
                        name="failing_tool",
                        arguments={},
                    )
                ],
            )
        ]
    )

    agent = Agent(
        llm=llm,
        tools=tools,
    )

    with pytest.raises(
        ToolExecutionError
    ):
        agent.run(
            "Use the failing tool."
        )

def test_llm_retry_then_success() -> None:

    llm = MockLLM(
        responses=[
            LLMTimeoutError(
                "temporary timeout"
            ),
            LLMResponse(
                content="Recovered.",
                model="mock",
                usage=usage(),
            ),
        ]
    )

    retry_policy = RetryPolicy(
        max_retries=1,
        backoff=ExponentialBackoff(
            initial_delay=0.0,
            multiplier=1.0,
            max_delay=0.0,
        ),
    )

    agent = Agent(
        llm=llm,
        retry_policy=retry_policy,
    )

    result = agent.run(
        "Hello"
    )

    assert (
        result.answer
        == "Recovered."
    )

    assert len(
        llm.requests
    ) == 2

def test_repeated_tool_call_is_blocked() -> None:

    repeated_call = ToolCall(
        id="same-call",
        name="add",
        arguments={
            "a": 1,
            "b": 1,
        },
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock",
                usage=usage(),
                tool_calls=[
                    repeated_call
                ],
            ),
            LLMResponse(
                content=None,
                model="mock",
                usage=usage(),
                tool_calls=[
                    repeated_call
                ],
            ),
            LLMResponse(
                content=None,
                model="mock",
                usage=usage(),
                tool_calls=[
                    repeated_call
                ],
            ),
        ]
    )

    tools = ToolRegistry()

    tools.register(
        AddTool()
    )

    agent = Agent(
        llm=llm,
        tools=tools,
        loop_policy=LoopPolicy(
            max_repeated_actions=2
        ),
        max_steps=10,
    )

    with pytest.raises(
        RepeatedActionError
    ):
        agent.run(
            "Keep adding."
        )