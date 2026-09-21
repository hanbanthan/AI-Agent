from agent_engineer.agent import AgentStep, StepType, Trajectory
from agent_engineer.llm import LLMResponse


def test_trajectory_adds_steps() -> None:
    trajectory = Trajectory()

    response = LLMResponse(
        content="Hello",
        model="mock-model",
    )

    step = AgentStep(
        step_number=1,
        step_type=StepType.FINAL,
        response=response,
    )

    trajectory.add(step)

    assert len(trajectory) == 1
    assert trajectory.steps[0] == step