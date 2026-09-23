from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class EvaluationResult:
    case_id: str

    task_success: bool

    answer_correct: bool

    tool_accuracy: float
    tool_efficiency: float

    step_count: int

    latency_ms: float

    input_tokens: int
    output_tokens: int
    total_tokens: int

    cost: float | None

    weighted_score: float | None

    error_type: str | None = None
    error_message: str | None = None

    details: dict[str, Any] = field(default_factory=dict)