from dataclasses import dataclass

class BudgetExceededError(Exception):
    pass

@dataclass(frozen=True)
class RequestBudget:
    max_tokens: int | None = None
    max_cost: float | None = None
    max_steps: int | None = None

@dataclass
class BudgetUsage:
    tokens: int = 0
    cost: float = 0.0
    steps: int = 0

class BudgetManager:

    def __init__(
        self,
        budget: RequestBudget,
    ) -> None:

        self.budget = budget
        self.usage = BudgetUsage()

    def record_tokens(
        self,
        tokens: int,
    ) -> None:

        self.usage.tokens += tokens
        self._validate()

    def record_cost(
        self,
        cost: float,
    ) -> None:

        self.usage.cost += cost
        self._validate()

    def record_step(self) -> None:
        self.usage.steps += 1
        self._validate()

    def _validate(self) -> None:

        if (
            self.budget.max_tokens is not None
            and self.usage.tokens > self.budget.max_tokens
        ):
            raise BudgetExceededError(
                f"Token budget exceeded: {self.usage.tokens} > {self.budget.max_tokens}"
            )
        
        if (
            self.budget.max_cost is not None
            and self.usage.cost > self.budget.max_cost
        ):
            raise BudgetExceededError(
                f"Cost budget exceeded: {self.usage.cost} > {self.budget.max_cost}"
            )

        if (
            self.budget.max_steps is not None
            and self.usage.steps > self.budget.max_steps
        ):
            raise BudgetExceededError(
                f"Step budget exceeded: {self.usage.steps} > {self.budget.max_steps}"
            )

@dataclass(frozen=True)
class EarlyStoppingPolicy:
    max_no_progress_steps: int = 2

    def should_stop(
        self,
        *,
        task_complete: bool,
        no_progress_steps: int,
    ) -> bool:

        if task_complete:
            return True

        return (
            no_progress_steps >= self.max_no_progress_steps
        )
    
