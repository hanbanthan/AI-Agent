import pytest
from agent_engineer.planning.replanning import ReplanningPlanner
from agent_engineer.planning import Plan, PlanStep

def test_observation_does_not_require_replanning() -> None:

    planner = ReplanningPlanner(
        plan_fn=lambda goal: Plan(
            steps=[
                PlanStep("Search"),
                PlanStep("Answer"),
            ]
        ),
        should_replan_fn=lambda plan, observation: False,
        replan_fn=lambda goal, plan, observation: plan,
    )

    plan = planner.create_plan("Research AI")

    should_replan = planner.should_replan(
        plan,
        observation="Search succeeded",
    )

    assert should_replan is False

def test_observation_triggers_replanning() -> None:

    planner = ReplanningPlanner(
        plan_fn=lambda goal: Plan(
            steps=[
                PlanStep("Use API A"),
                PlanStep("Write answer"),
            ]
        ),
        should_replan_fn=(
            lambda plan, observation:
            observation == "API unavailable"
        ),
        replan_fn=(
            lambda goal, plan, observation:
            Plan(
                steps=[
                    PlanStep("Use API B"),
                    PlanStep("Write answer"),
                ]
            )
        ),
    )

    old_plan = planner.create_plan("Research AI")

    assert planner.should_replan(
        old_plan,
        "API unavailable",
    )

    old_plan.invalidate()

    new_plan = planner.replan(
        goal="Research AI",
        plan=old_plan,
        observation="API unavailable",
    )

    assert old_plan.is_invalid

    assert (
        new_plan.steps[0].description
        == "Use API B"
    )