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