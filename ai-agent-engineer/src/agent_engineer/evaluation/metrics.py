from collections import Counter
from dataclasses import dataclass

from agent_engineer.evaluation.case import (
    AnswerConstraints,
)

def answer_matches(
    answer: str | None,
    constraints: AnswerConstraints,
) -> bool:

    if answer is None:
        return not (
            constraints.exact
            or constraints.contains_all
            or constraints.contains_any
            or constraints.not_contains
        )

    normalized = answer.lower()

    if constraints.exact is not None:
        if answer != constraints.exact:
            return False

    for value in constraints.contains_all:
        if value.lower() not in normalized:
            return False

    if constraints.contains_any:
        if not any(value.lower() in normalized for value in constraints.contains_any):
            return False

    for value in constraints.not_contains:
        if value.lower() in normalized:
            return False

    return True

def tool_accuracy_score(
    expected: list[str],
    actual: list[str],
) -> float:

    if not expected:
        return 1.0 if not actual else 0.0

    if not actual:
        return 0.0

    expected_counter = Counter(expected)
    actual_counter = Counter(actual)

    true_positives = sum(
        min(expected_counter[tool], actual_counter[tool])
        for tool in expected_counter
    )

    precision = true_positives / len(actual)

    recall = true_positives / len(expected)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)

def tool_efficiency_score(
    expected: list[str],
    actual: list[str],
) -> float:

    expected_count = len(expected)
    actual_count = len(actual)

    if expected_count == 0:
        return 1.0 if actual_count == 0 else 0.0
    if actual_count == 0:
        return 0.0
    return min(1.0, expected_count / actual_count)

@dataclass(frozen=True)
class ScoreWeights:
    task_success: float
    tool_accuracy: float
    tool_efficiency: float

    def __post_init__(self):
        total = (
            self.task_success
            + self.tool_accuracy
            + self.tool_efficiency
        )

        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                "The sum of task_success, tool_accuracy, and tool_efficiency weights must equal 1.0."
            )

def weighted_score(
    task_success: bool,
    tool_accuracy: float,
    tool_efficiency: float,
    weights: ScoreWeights,
) -> float:

    return (
        weights.task_success * float(task_success)
        + weights.tool_accuracy * tool_accuracy
        + weights.tool_efficiency * tool_efficiency
    )