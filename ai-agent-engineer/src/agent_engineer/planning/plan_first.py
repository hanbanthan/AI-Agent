from collections.abc import Callable

from agent_engineer.planning.types import Plan
from agent_engineer.planning.base import Planner

class PlanFirstPlanner(Planner):
    def __init__(
        self,
        plan_fn: Callable[[str], Plan],
    ) -> None:
        self._plan_fn = plan_fn

    def create_plan(self, goal: str) -> Plan:
        return self._plan_fn(goal)