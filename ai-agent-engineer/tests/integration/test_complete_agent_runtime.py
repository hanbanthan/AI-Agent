from agent_engineer.agent.agent import Agent
from agent_engineer.agent.trajectory import (
    StepType,
)

from agent_engineer.llm.mock import MockLLM
from agent_engineer.llm.types import (
    LLMResponse,
    Usage,
)

from agent_engineer.tools.registry import (
    ToolRegistry,
)
from agent_engineer.tools.types import (
    ToolCall,
)

from agent_engineer.observability.trace import (
    Tracer,
)

from tests.integration.helpers import (
    AddTool,
    MultiplyTool,
)

def usage(
    input_tokens: int = 10,
    output_tokens: int = 5,
) -> Usage:

    return Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

def test_simple_answer() -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Python is a programming language.",
                model="mock-model",
                usage=usage(),
            )
        ]
    )

    agent = Agent(
        llm=llm,
    )

    result = agent.run(
        "What is Python?"
    )

    assert (
        result.answer
        == "Python is a programming language."
    )

    assert result.steps == 1

def test_single_tool() -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock-model",
                usage=usage(),
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="add",
                        arguments={
                            "a": 2,
                            "b": 3,
                        },
                    )
                ],
            ),
            LLMResponse(
                content="The answer is 5.",
                model="mock-model",
                usage=usage(),
            ),
        ]
    )

    tools = ToolRegistry()

    tools.register(
        AddTool()
    )

    tracer = Tracer()

    agent = Agent(
        llm=llm,
        tools=tools,
        tracer=tracer,
    )

    result = agent.run(
        "What is 2 + 3?"
    )

    assert (
        result.answer
        == "The answer is 5."
    )

    assert result.steps == 2
    assert result.trace is not None

    observations = [
        step
        for step
        in result.trajectory.steps
        if (
            step.step_type
            == StepType.OBSERVATION
        )
    ]

    assert len(observations) == 1

    assert (
        observations[0].data.output
        == 5
    )

    span_names = [
        span.name
        for span
        in result.trace.spans
    ]

    assert span_names == [
        "llm",
        "tool.add",
        "llm",
    ]


def test_multiple_tools() -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock-model",
                usage=usage(),
                tool_calls=[
                    ToolCall(
                        id="call-add",
                        name="add",
                        arguments={
                            "a": 2,
                            "b": 3,
                        },
                    ),
                    ToolCall(
                        id="call-multiply",
                        name="multiply",
                        arguments={
                            "a": 4,
                            "b": 5,
                        },
                    ),
                ],
            ),
            LLMResponse(
                content=(
                    "The results are "
                    "5 and 20."
                ),
                model="mock-model",
                usage=usage(),
            ),
        ]
    )

    tools = ToolRegistry()

    tools.register(
        AddTool()
    )

    tools.register(
        MultiplyTool()
    )

    agent = Agent(
        llm=llm,
        tools=tools,
    )

    result = agent.run(
        "Calculate 2+3 and 4*5."
    )

    observations = [
        step.data.output
        for step
        in result.trajectory.steps
        if (
            step.step_type
            == StepType.OBSERVATION
        )
    ]

    assert observations == [
        5,
        20,
    ]

    assert (
        result.answer
        == "The results are 5 and 20."
    )