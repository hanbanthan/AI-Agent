from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class EvaluationCategory(str, Enum):
    NORMAL = "normal"
    EDGE = "edge"
    ADVERSARIAL = "adversarial"
    TOOL_FAILURE = "tool_failure"

class FailureMode(str, Enum):
    NONE = "none"
    RAISE = "raise"
    RECOVER = "recover"

@dataclass(frozen=True)
class AnswerConstraints:
    exact: str | None = None
    contains_all: tuple[str, ...] = ()
    contains_any: tuple[str, ...] = ()
    not_contains: tuple[str, ...] = ()

@dataclass(frozen=True)
class ExpectedFailureBehavior:
    mode: FailureMode = FailureMode.NONE
    allowed_error_types: tuple[str, ...] = ()

@dataclass(frozen=True)
class EvaluationCase:
    id: str
    category: EvaluationCategory
    input: str

    expected_tools: tuple[str, ...] = ()
    forbidden_tools: tuple[str, ...] = ()

    answer: AnswerConstraints = field(
        default_factory=AnswerConstraints
    )

    expected_failure: ExpectedFailureBehavior = field(
        default_factory=ExpectedFailureBehavior
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.id.strip():
            raise ValueError("EvaluationCase id must be a non-empty string.")

        if not self.input.strip():
            raise ValueError("EvaluationCase input must be a non-empty string.")

        overlap = set(self.expected_tools) & set(self.forbidden_tools)

        if overlap:
            raise ValueError(
                f"EvaluationCase expected_tools and forbidden_tools "
                f"must not overlap. Overlapping tools: {overlap}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationCase":

        answer_data = data.get("answer", {})

        failure_data = data.get("expected_failure", {})

        case = cls(
            id=data["id"],
            category=EvaluationCategory(data["category"]),
            input=data["input"],
            expected_tools=tuple(data.get("expected_tools", ())),
            forbidden_tools=tuple(data.get("forbidden_tools", ())),
            answer=AnswerConstraints(
                exact=answer_data.get("exact"),
                contains_all=tuple(answer_data.get("contains_all", ())),
                contains_any=tuple(answer_data.get("contains_any", ())),
                not_contains=tuple(answer_data.get("not_contains", ())),
            ),
            expected_failure=ExpectedFailureBehavior(
                mode=FailureMode(failure_data.get("mode", "none")),
                allowed_error_types=tuple(failure_data.get("allowed_error_types", ())),
            ),
            metadata=data.get("metadata", {}),
        )

        case.validate()

        return case
        