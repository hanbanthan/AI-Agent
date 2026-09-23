from agent_engineer.agent.agent import (
    AgentResult,
)
from agent_engineer.agent.trajectory import (
    AgentStep,
    StepType,
    Trajectory,
)
from agent_engineer.tools.types import ToolCall

from agent_engineer.evaluation import (
    AnswerConstraints,
    EvaluationCase,
    EvaluationCategory,
    ScoreWeights,
    TrajectoryEvaluator,
)

def make_result(
    answer: str,
    tool_names: list[str],
) -> AgentResult:

    trajectory = Trajectory()

    for index, name in enumerate(
        tool_names,
        start=1,
    ):
        trajectory.add(
            AgentStep(
                step_number=index,
                step_type=StepType.TOOL_CALL,
                data=ToolCall(
                    name=name,
                    arguments={},
                ),
            )
        )

    return AgentResult(
        answer=answer,
        trajectory=trajectory,
        steps=len(tool_names) + 1,
    )

def make_evaluator() -> TrajectoryEvaluator:
    return TrajectoryEvaluator(
        weights=ScoreWeights(
            task_success=0.6,
            tool_accuracy=0.25,
            tool_efficiency=0.15,
        )
    )

def test_perfect_trajectory() -> None:

    case = EvaluationCase(
        id="perfect",
        category=EvaluationCategory.NORMAL,
        input="Calculate",
        expected_tools=("calculator",),
        answer=AnswerConstraints(
            contains_all=("5",)
        ),
    )

    result = make_result(
        answer="The answer is 5.",
        tool_names=["calculator"],
    )

    evaluation = make_evaluator().evaluate(
        case=case,
        result=result,
        error=None,
        latency_ms=10,
    )

    assert evaluation.task_success is True
    assert evaluation.tool_accuracy == 1.0
    assert evaluation.tool_efficiency == 1.0
    assert evaluation.weighted_score == 1.0

def test_wrong_tool() -> None:

    case = EvaluationCase(
        id="wrong-tool",
        category=EvaluationCategory.NORMAL,
        input="Calculate",
        expected_tools=("calculator",),
        answer=AnswerConstraints(
            contains_all=("5",)
        ),
    )

    result = make_result(
        answer="5",
        tool_names=["search"],
    )

    evaluation = make_evaluator().evaluate(
        case=case,
        result=result,
        error=None,
        latency_ms=1,
    )

    assert evaluation.answer_correct is True
    assert evaluation.tool_accuracy == 0.0

def test_redundant_tool() -> None:

    case = EvaluationCase(
        id="redundant",
        category=EvaluationCategory.NORMAL,
        input="Calculate",
        expected_tools=("calculator",),
        answer=AnswerConstraints(
            contains_all=("5",)
        ),
    )

    result = make_result(
        answer="5",
        tool_names=[
            "calculator",
            "calculator",
        ],
    )

    evaluation = make_evaluator().evaluate(
        case=case,
        result=result,
        error=None,
        latency_ms=1,
    )

    assert evaluation.tool_accuracy < 1.0
    assert evaluation.tool_efficiency == 0.5

def test_failed_answer() -> None:

    case = EvaluationCase(
        id="failed-answer",
        category=EvaluationCategory.NORMAL,
        input="2 + 3?",
        expected_tools=("calculator",),
        answer=AnswerConstraints(
            contains_all=("5",)
        ),
    )

    result = make_result(
        answer="The answer is 7.",
        tool_names=["calculator"],
    )

    evaluation = make_evaluator().evaluate(
        case=case,
        result=result,
        error=None,
        latency_ms=1,
    )

    assert evaluation.answer_correct is False
    assert evaluation.task_success is False

def test_forbidden_tool_fails_task() -> None:

    case = EvaluationCase(
        id="adversarial",
        category=EvaluationCategory.ADVERSARIAL,
        input="Do not perform unsafe action",
        forbidden_tools=("send_email",),
    )

    result = make_result(
        answer="Done.",
        tool_names=["send_email"],
    )

    evaluation = make_evaluator().evaluate(
        case=case,
        result=result,
        error=None,
        latency_ms=1,
    )

    assert evaluation.task_success is False

from agent_engineer.evaluation import (
    ExpectedFailureBehavior,
    FailureMode,
)
from agent_engineer.tools.errors import (
    ToolExecutionError,
)


def test_expected_tool_failure() -> None:

    case = EvaluationCase(
        id="tool-failure",
        category=EvaluationCategory.TOOL_FAILURE,
        input="Search",
        expected_failure=(
            ExpectedFailureBehavior(
                mode=FailureMode.RAISE,
                allowed_error_types=(
                    "ToolExecutionError",
                ),
            )
        ),
    )

    evaluation = make_evaluator().evaluate(
        case=case,
        result=None,
        error=ToolExecutionError(
            "Search unavailable"
        ),
        latency_ms=1,
    )

    assert evaluation.task_success is True