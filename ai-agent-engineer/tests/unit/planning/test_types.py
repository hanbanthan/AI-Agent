from agent_engineer.planning import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)

from agent_engineer.planning.replanning import ReplanningPlanner



def test_plan_steps_complete_in_order() -> None:

    plan = Plan(
        steps=[
            PlanStep("Step A"),
            PlanStep("Step B"),
            PlanStep("Step C"),
        ]
    )

    plan.start()

    assert plan.current_step.description == "Step A"

    plan.complete_current_step()

    assert plan.current_step.description == "Step B"

    plan.complete_current_step()

    assert plan.current_step.description == "Step C"

    plan.complete_current_step()

    assert plan.current_step is None
    assert plan.status == PlanStatus.COMPLETED

def test_plan_can_be_invalidated() -> None:

    plan = Plan(
        steps=[
            PlanStep("Search API"),
            PlanStep("Call API"),
        ]
    )

    plan.start()

    plan.invalidate()

    assert plan.is_invalid is True