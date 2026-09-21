from dataclasses import dataclass
from enum import Enum

class PlanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INVALID = "invalid"

class PlanStepStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class PlanStep:
    description: str
    status: PlanStepStatus = PlanStepStatus.PENDING

    @property
    def is_completed(self) -> bool:
        return self.status == PlanStepStatus.COMPLETED

    def complete(self) -> None:
        self.status = PlanStepStatus.COMPLETED

@dataclass
class Plan:
    steps: list[PlanStep]
    status: PlanStatus = PlanStatus.PENDING
    current_step_index: int = 0

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("A plan must have at least one step.")

    @property
    def current_step(self) -> PlanStep | None:
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    @property
    def is_completed(self) -> bool:
        return self.status == PlanStatus.COMPLETED

    @property
    def is_invalid(self) -> bool:
        return self.status == PlanStatus.INVALID

    def start(self) -> None:
        if self.status == PlanStatus.PENDING:
            self.status = PlanStatus.IN_PROGRESS

    def complete_current_step(self) -> None:
        step = self.current_step

        if step is None:
            return

        step.complete()
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self.status = PlanStatus.COMPLETED

    def invalidate(self) -> None:
        self.status = PlanStatus.INVALID

    def to_text(self) -> str:
        lines: list[str] = []
        for index, step in enumerate(self.steps, start=1):
            marker = "[X]" if step.is_completed else "[ ]"
            lines.append(f"{marker} Step {index}: {step.description}")
        return "\n".join(lines)
    