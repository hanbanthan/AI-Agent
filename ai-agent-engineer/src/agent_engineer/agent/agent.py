from dataclasses import dataclass

from agent_engineer.agent.loop import AgentLoop
from agent_engineer.agent.state import AgentState
from agent_engineer.agent.trajectory import Trajectory
from agent_engineer.llm.base import LLM
from agent_engineer.llm.types import Message
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.planning.base import Planner

@dataclass(frozen=True)
class AgentResult:
    answer: str
    trajectory: Trajectory
    steps: int

class Agent:
    def __init__(
        self,
        llm: LLM,
        tool_executor: ToolExecutor | None = None,
        planner: Planner | None = None,
        max_steps: int = 10,
    ) -> None:
        self._loop = AgentLoop(
            llm=llm, tool_executor=tool_executor, planner=planner, max_steps=max_steps)

    def run(self, user_input: str) -> AgentResult:
        state = AgentState(
            messages=[
                Message(
                    role="user",
                    content=user_input,
                )
            ]
        )

        state = self._loop.run(state, goal=user_input)

        return AgentResult(
            answer=state.final_answer or "",
            trajectory=state.trajectory,
            steps=state.step_count,
        )