from dataclasses import dataclass


from agent_engineer.agent.loop import AgentLoop
from agent_engineer.agent.state import AgentState
from agent_engineer.agent.trajectory import Trajectory
from agent_engineer.llm.base import LLM
from agent_engineer.llm.types import Message
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.planning.base import Planner
from agent_engineer.memory.manager import MemoryManager
from agent_engineer.resilience.retry import RetryPolicy
from agent_engineer.agent.loop_guard import LoopPolicy
from agent_engineer.security.guardrails import SecurityGuard
from agent_engineer.security.policy import SecurityContext
from agent_engineer.observability.trace import Trace
from agent_engineer.observability.trace import Tracer

@dataclass(frozen=True)
class AgentResult:
    answer: str
    trajectory: Trajectory
    steps: int
    trace: Trace | None = None

class Agent:
    def __init__(
        self,
        llm: LLM,
        tool_executor: ToolExecutor | None = None,
        planner: Planner | None = None,
        memory_manager: MemoryManager | None = None,
        retry_policy: RetryPolicy | None = None,
        loop_policy: LoopPolicy | None = None,
        security_guard: SecurityGuard | None = None,
        tracer: Tracer | None = None,
        max_steps: int = 10,
    ) -> None:
        self._loop = AgentLoop(
            llm=llm, 
            tool_executor=tool_executor, 
            planner=planner,  
            memory_manager=memory_manager,
            retry_policy=retry_policy,
            loop_policy=loop_policy,
            security_guard=security_guard,
            tracer = tracer,
            max_steps=max_steps)

    def run(
        self, 
        user_input: str, 
        security_context: SecurityContext | None = None
    ) -> AgentResult:
        user_message = Message(
            role="user",
            content=user_input,
        )

        state = AgentState(
            messages=[user_message]
        )

        state = self._loop.run(
            state=state, 
            goal=user_input, 
            security_context=security_context
        )

        if self._loop.memory_manager:
            self._loop.memory_manager.remember_message(user_message)

        return AgentResult(
            answer=state.final_answer or "",
            trajectory=state.trajectory,
            steps=state.step_count,
        )   


    