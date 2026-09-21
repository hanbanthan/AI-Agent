from abc import ABC, abstractmethod
from typing import Any

from agent_engineer.planning.types import Plan

class Planner(ABC):

    @abstractmethod
    def create_plan(self, goal: str) -> Plan:
        raise NotImplementedError

    def should_replan(
            self,
            plan: Plan,
            observation: Any,
    ) -> bool:
        return False

    def replan(
            self,
            goal: str,
            plan: Plan,
            observation: Any,
    ) -> Plan:
        return plan

    @property
    def max_replans(self) -> int:
        return 0