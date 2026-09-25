import pytest

from agent_engineer.optimization.budget import (
    BudgetExceededError,
    BudgetManager,
    RequestBudget,
    EarlyStoppingPolicy,
)

def test_budget_exceeded() -> None:

    manager = BudgetManager(
        budget=RequestBudget(
            max_tokens=100,
        )
    )

    manager.record_tokens(70)

    with pytest.raises(BudgetExceededError):
        manager.record_tokens(40)

def test_early_stopping() -> None:

    policy  = EarlyStoppingPolicy(
        max_no_progress_steps=2,
    )

    assert(
        policy.should_stop(
            task_complete=False,
            no_progress_steps=1,
        ) 
        is False
    )

    assert(
        policy.should_stop(
            task_complete=False,
            no_progress_steps=2,
        )
        is True
    )
