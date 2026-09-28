from agent_engineer.agent import Agent
from agent_engineer.llm import (
    LLMResponse,
    MockLLM,
)
from agent_engineer.planning import (
    Plan,
    PlanFirstPlanner,
    PlanStep,
)

from dataclasses import dataclass

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

from tests.integration.helpers import (
    AddTool,
)


def test_agent_without_planner_still_works() -> None:
    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Hello!",
                model="mock-model",
            )
        ]
    )

    agent = Agent(llm=llm)

    result = agent.run("Hello")

    assert result.answer == "Hello!"


def test_agent_includes_plan_in_llm_request() -> None:
    planner = PlanFirstPlanner(
        plan_fn=lambda goal: Plan(
            steps=[
                PlanStep("Research topic"),
                PlanStep("Write answer"),
            ]
        )
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Final answer",
                model="mock-model",
            )
        ]
    )

    agent = Agent(
        llm=llm,
        planner=planner,
    )

    agent.run("Explain AI agents")

    request = llm.requests[0]

    assert request.messages[0].role == "system"
    assert "Research topic" in request.messages[0].content

@dataclass
class FakePlan:
    text: str
    started: bool = False
    invalid: bool = False
    completed_steps: int = 0

    def start(self) -> None:
        self.started = True

    def invalidate(self) -> None:
        self.invalid = True

    def complete_current_step(
        self,
    ) -> None:
        self.completed_steps += 1

    def to_text(self) -> str:
        return self.text

class FakePlanner:

    def __init__(
        self,
        should_replan: bool = False,
    ) -> None:

        self.max_replans = 1
        self._should_replan = (
            should_replan
        )

        self.create_count = 0
        self.replan_count = 0

    def create_plan(
        self,
        goal: str,
    ) -> FakePlan:

        self.create_count += 1

        return FakePlan(
            text=f"Plan for: {goal}"
        )

    def should_replan(
        self,
        plan: FakePlan,
        observation: object,
    ) -> bool:
        return self._should_replan

    def replan(
        self,
        goal: str,
        plan: FakePlan,
        observation: object,
    ) -> FakePlan:

        self.replan_count += 1

        return FakePlan(
            text=(
                f"Replanned for: {goal}"
            )
        )

def usage() -> Usage:
    return Usage(
        input_tokens=10,
        output_tokens=5,
    )

def test_agent_creates_plan() -> None:

    planner = FakePlanner()

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Done.",
                model="mock",
                usage=usage(),
            )
        ]
    )

    agent = Agent(
        llm=llm,
        planner=planner,
    )

    result = agent.run(
        "Complete the task."
    )

    plan_steps = [
        step
        for step
        in result.trajectory.steps
        if (
            step.step_type
            == StepType.PLAN
        )
    ]

    assert planner.create_count == 1
    assert len(plan_steps) == 1

    assert (
        plan_steps[0]
        .data
        .started
        is True
    )

def test_agent_replans_after_observation() -> None:

    planner = FakePlanner(
        should_replan=True
    )

    tools = ToolRegistry()

    tools.register(
        AddTool()
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock",
                usage=usage(),
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
                content="Finished.",
                model="mock",
                usage=usage(),
            ),
        ]
    )

    agent = Agent(
        llm=llm,
        tools=tools,
        planner=planner,
    )

    result = agent.run(
        "Do the task."
    )

    replan_steps = [
        step
        for step
        in result.trajectory.steps
        if (
            step.step_type
            == StepType.REPLAN
        )
    ]

    assert planner.replan_count == 1
    assert len(replan_steps) == 1