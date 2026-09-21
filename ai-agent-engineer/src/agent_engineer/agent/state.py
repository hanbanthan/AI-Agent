from dataclasses import dataclass, field

from agent_engineer.agent.trajectory import Trajectory
from agent_engineer.llm.types import Message
from agent_engineer.planning.types import Plan

@dataclass
class AgentState:
    messages: list[Message] = field(default_factory=list)
    trajectory: Trajectory = field(default_factory=Trajectory)

    plan: Plan | None = None
    replan_count: int = 0

    step_count: int = 0
    finished: bool = False
    final_answer: str | None = None

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def increment_step(self) -> None:
        self.step_count += 1

    def finish(self, answer: str = "") -> None:
        self.finished = True
        self.final_answer = answer

    def mark_finished(self, answer: str = "") -> None:
        self.finish(answer=answer)
