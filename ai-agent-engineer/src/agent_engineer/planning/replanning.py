from collections.abc import Callable
from typing import Any

from agent_engineer.planning.types import Plan
from agent_engineer.planning.base import Planner

class ReplanningPlanner(Planner):

    def __init__(
        self,
        plan_fn: Callable[[str], Plan],
        should_replan_fn: Callable[[Plan, Any], bool],
        replan_fn: Callable[[str, Plan, Any], Plan],
        max_replans: int = 3,
    ) -> None:
        if max_replans < 0:
            raise ValueError("max_replans must be non-negative")
        self._plan_fn = plan_fn
        self._should_replan_fn = should_replan_fn
        self._replan_fn = replan_fn
        self._max_replans = max_replans

    def create_plan(self, goal: str) -> Plan:
        return self._plan_fn(goal)

    def should_replan(
            self,
            plan: Plan,
            observation: Any,
    ) -> bool:
        return self._should_replan_fn(plan, observation)

    def replan(
            self,
            goal: str,
            plan: Plan,
            observation: Any,
    ) -> Plan:
        return self._replan_fn(goal, plan, observation)

    @property
    def max_replans(self) -> int:
        return self._max_replans