from abc import ABC, abstractmethod
from collections.abc import Callable

from agent_engineer.agent.agent import (
    AgentResult,
)
from agent_engineer.agent.trajectory import (
    StepType,
)
from agent_engineer.evaluation.case import (
    EvaluationCase,
    FailureMode,
)
from agent_engineer.evaluation.metrics import (
    ScoreWeights,
    answer_matches,
    tool_accuracy_score,
    tool_efficiency_score,
    weighted_score,
)
from agent_engineer.evaluation.result import (
    EvaluationResult,
)
from agent_engineer.llm.types import (
    LLMResponse,
)

class Evaluator(ABC):

    @abstractmethod
    def evaluate(
        self,
        *,
        case: EvaluationCase,
        result: AgentResult | None,
        error: Exception | None,
        latency_ms: float | None,
    ) -> EvaluationResult:
        raise NotImplementedError

class TrajectoryEvaluator(Evaluator):

    def __init__(
        self,
        weights: ScoreWeights,
        cost_fn: (
            Callable[[LLMResponse], float]
            | None
        ) = None,
    ) -> None:
        self.weights = weights
        self.cost_fn = cost_fn

    def evaluate(
        self,
        *,
        case: EvaluationCase,
        result: AgentResult | None,
        error: Exception | None,
        latency_ms: float,
    ) -> EvaluationResult:

        actual_tools: list[str] = []

        input_tokens = 0
        output_tokens = 0

        cost: float | None = (
            0.0 
            if self.cost_fn is not None 
            else None
        )

        if result is not None:

            for step in result.trajectory.steps:
                if (step.step_type == StepType.TOOL_CALL):
                    actual_tools.append(step.data.name)

                if isinstance(step.data, LLMResponse):
                    input_tokens += step.data.usage.input_tokens

                    output_tokens += step.data.usage.output_tokens

                    if (self.cost_fn is not None and cost is not None):
                        cost += self.cost_fn(step.data)

        tool_accuracy = tool_accuracy_score(
            list(case.expected_tools),
            actual_tools,
        )

        tool_efficiency = tool_efficiency_score(
            list(case.expected_tools),
            actual_tools,
        )

        forbidden_used = bool(
            set(actual_tools) & set(case.forbidden_tools)
        )

        answer = (
            result.answer
            if result is not None
            else None
        )

        answer_correct = answer_matches(
            answer,
            case.answer,
        )

        failure_correct = (
            self._failure_matches(
                case=case,
                error=error,
            )
        )

        task_success = (
            answer_correct
            and failure_correct
            and not forbidden_used
        )

        score = weighted_score(
            task_success=task_success,
            tool_accuracy=tool_accuracy,
            tool_efficiency=tool_efficiency,
            weights=self.weights,
        )

        step_count = (
            result.steps
            if result is not None
            else 0
        )

        return EvaluationResult(
            case_id=case.id,
            task_success=task_success,
            answer_correct=answer_correct,
            tool_accuracy=tool_accuracy,
            tool_efficiency=tool_efficiency,
            step_count=step_count,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            weighted_score=score,
            error_type=(
                type(error).__name__
                if error is not None
                else None
            ),
            error_message=(
                str(error)
                if error is not None
                else None
            ),
            details={
                "expected_tools": case.expected_tools,
                "actual_tools": actual_tools,
                "forbidden_tools_used": forbidden_used,
                "failure_correct": failure_correct,
            }
        )

    def _failure_matches(
        self,
        *,
        case: EvaluationCase,
        error: Exception | None,
    ) -> bool:

        expected = case.expected_failure

        if expected.mode == FailureMode.NONE:
            return error is None

        if expected.mode == FailureMode.RECOVER:
            return error is None

        if error is None:
            return False

        if not expected.allowed_error_types:
            return True

        return (
            type(error).__name__ in expected.allowed_error_types
        )



