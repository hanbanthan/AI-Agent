from agent_engineer.planning import (
    Plan,
    PlanFirstPlanner,
    PlanStep,
)


def test_plan_first_creates_plan() -> None:

    planner = PlanFirstPlanner(
        plan_fn=lambda goal: Plan(
            steps=[
                PlanStep(f"Research {goal}"),
                PlanStep("Write answer"),
            ]
        )
    )

    plan = planner.create_plan("AI agents")

    assert len(plan.steps) == 2
    assert plan.steps[0].description == (
        "Research AI agents"
    )