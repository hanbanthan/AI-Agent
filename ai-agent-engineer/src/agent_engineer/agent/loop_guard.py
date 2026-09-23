import json

from dataclasses import dataclass

from agent_engineer.agent.errors import (
    RepeatedActionError,
)

from agent_engineer.tools.types import ToolCall

@dataclass(frozen=True)
class LoopPolicy:
    max_repeated_actions: int = 3

    def __post_init__(self) -> None:
        if self.max_repeated_actions <= 0:
            raise ValueError("max_repeated_actions must be a positive integer.")

class LoopDetector:

    def __init__(
        self,
        policy: LoopPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            if policy is not None
            else LoopPolicy()
        )

        self._last_fingerprint: str | None = None
        self._repeated_count: int = 0

    def record_tool_call(
        self,
        call: ToolCall,
    ) -> None:

        fingerprint = self._fingerprint(call)

        if fingerprint == self._last_fingerprint:
            self._repeated_count += 1
        else:
            self._last_fingerprint = fingerprint
            self._repeated_count = 1

        if (
            self._repeated_count > self.policy.max_repeated_actions
        ):
            raise RepeatedActionError(
                f"Repeated tool call detected: {call}. "
                f"Count: {self._repeated_count}, "
                f"Max allowed: {self.policy.max_repeated_actions}."
            )

    def _fingerprint(
        self,
        call: ToolCall,
    ) -> str:

        arguments = json.dumps(
            call.arguments,
            sort_keys=True,
            default=str,
        )

        return f"{call.name}:{arguments}"