from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agent_engineer.llm.types import LLMResponse, Message

class StepType(str, Enum):
    PLAN = "plan"
    REPLAN = "replan"
    LLM = "llm"
    TOOL_CALL = "tool_call"
    OBSERVATION = "observation"
    FINAL = "final"

@dataclass(frozen=True, init=False)
class AgentStep:
    step_number: int
    step_type: StepType
    data: Any

    def __init__(
        self,
        step_number: int,
        step_type: StepType,
        data: Any = None,
        *,
        response: Any = None,
        rdata: Any = None,
    ) -> None:
        payload = data
        if data is None:
            if response is not None:
                payload = response
            elif rdata is not None:
                payload = rdata

        object.__setattr__(self, "step_number", step_number)
        object.__setattr__(self, "step_type", step_type)
        object.__setattr__(self, "data", payload)

    @property
    def response(self) -> Any:
        return self.data

    @property
    def rdata(self) -> Any:
        return self.data

@dataclass
class Trajectory:
    steps: list[AgentStep] = field(default_factory=list)

    def add(self, step: AgentStep) -> None:
        self.steps.append(step)

    def __len__(self) -> int:
        return len(self.steps)