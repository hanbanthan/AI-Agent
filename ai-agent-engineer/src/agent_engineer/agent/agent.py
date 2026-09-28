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

from agent_engineer.llm.types import LLMResponse
from agent_engineer.tools.types import ToolCall
from agent_engineer.tools.types import ToolResult

from agent_engineer.tools.registry import ToolRegistry
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.optimization.budget import BudgetManager

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
        tools: ToolRegistry | None = None,
        planner: Planner | None = None,
        memory: MemoryManager | None = None,
        tracer: Tracer | None = None,
        security: SecurityGuard | None = None,
        budget: BudgetManager | None = None,
        retry_policy: RetryPolicy | None = None,
        loop_policy: LoopPolicy | None = None,
        max_steps: int = 10,
    ) -> None:

        tool_executor = (
            ToolExecutor(tools)
            if tools is not None
            else None
        )

        self.memory = memory
        self.tracer = tracer

        self._loop = AgentLoop(
            llm=llm,
            tool_executor=tool_executor,
            planner=planner,
            memory_manager=memory,
            retry_policy=retry_policy,
            loop_policy=loop_policy,
            security_guard=security,
            tracer=tracer,
            budget=budget,
            max_steps=max_steps,
        )

    def run(
        self, 
        user_input: str, 
        security_context: SecurityContext | None = None
    ) -> AgentResult:
        user_message = Message(
            role="user",
            content=user_input,
            tool_calls=[],
        )

        state = AgentState(
            messages=[user_message]
        )

        trace = None

        if self.tracer is None:

            state = self._loop.run(
                state=state,
                goal=user_input,
                security_context=security_context,
            )
        
        else:
            with self.tracer.trace("agent") as trace:
                state = self._loop.run(
                    state=state,
                    goal=user_input,
                    security_context=security_context,
                )

        if (
            self.memory is not None
        ): 
            self.memory.remember_message(
                message=user_message
            )

        return AgentResult(
            answer=state.final_answer,
            trajectory=state.trajectory,
            steps=state.step_count,
            trace=trace,
        )

    #--------------------------------------------------------
    # EXPLICIT AGENT PRIMITIVES
    #
    # These methods make it clear what an Agent framework 
    # normally abtracts
    #--------------------------------------------------------

    def plan(
        self,
        state: AgentState,
        goal: str,
    ) -> None:

        self._loop.plan(
            state=state,
            goal=goal,
        )

    def select_tool(
        self,
        response: LLMResponse,
    ) -> list[ToolCall]:

        return self._loop.select_tool(
            response=response,
        )

    def execute_tool(
        self,
        tool_call: ToolCall,
        security_context: SecurityContext | None = None,
    ) -> ToolResult:

        context = (
            security_context
            if security_context is not None
            else SecurityContext()
        )

        # Standalone public call
        # Runtime run() uses its own per-run detector

        return self._loop.execute_tool(
            tool_call=tool_call,
            security_context=context,
            loop_detector=None,
        )

    def observe(
        self,
        state: AgentState,
        tool_call: ToolCall,
        result: ToolResult,
    ) -> None:

        self._loop.observe(
            state=state,
            tool_call=tool_call,
            result=result,
        )

    def should_stop(
        self,
        state: AgentState,
    ) -> bool:

        return self._loop.should_stop(
            state=state,
        )

        