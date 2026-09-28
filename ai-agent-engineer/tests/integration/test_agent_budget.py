import pytest

from agent_engineer.agent.agent import Agent

from agent_engineer.llm.mock import MockLLM
from agent_engineer.llm.types import (
    LLMResponse,
    Usage,
)

from agent_engineer.optimization.budget import (
    BudgetExceededError,
    BudgetManager,
    RequestBudget,
)

from agent_engineer.tools.registry import (
    ToolRegistry,
)
from agent_engineer.tools.types import (
    ToolCall,
)

from tests.integration.helpers import (
    AddTool,
)

def test_agent_token_budget_exceeded() -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Answer",
                model="mock",
                usage=Usage(
                    input_tokens=80,
                    output_tokens=30,
                ),
            )
        ]
    )

    budget = BudgetManager(
        RequestBudget(
            max_tokens=100
        )
    )

    agent = Agent(
        llm=llm,
        budget=budget,
    )

    with pytest.raises(
        BudgetExceededError
    ):
        agent.run(
            "Question"
        )

def test_agent_step_budget_exceeded() -> None:

    tools = ToolRegistry()

    tools.register(
        AddTool()
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock",
                usage=Usage(
                    input_tokens=10,
                    output_tokens=5,
                ),
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="add",
                        arguments={
                            "a": 1,
                            "b": 2,
                        },
                    )
                ],
            ),
            LLMResponse(
                content="Done.",
                model="mock",
                usage=Usage(
                    input_tokens=10,
                    output_tokens=5,
                ),
            ),
        ]
    )

    budget = BudgetManager(
        RequestBudget(
            max_steps=1
        )
    )

    agent = Agent(
        llm=llm,
        tools=tools,
        budget=budget,
        max_steps=10,
    )

    with pytest.raises(
        BudgetExceededError
    ):
        agent.run(
            "Complete this task."
        )
