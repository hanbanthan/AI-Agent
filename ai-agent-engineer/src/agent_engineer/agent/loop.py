

from agent_engineer.agent.errors import AgentError, MaxStepsExceededError
from agent_engineer.agent.state import AgentState
from agent_engineer.agent.trajectory import AgentStep, StepType
from agent_engineer.llm.base import LLM
from agent_engineer.llm.types import LLMRequest, LLMResponse, Message
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.planning.base import Planner
from agent_engineer.memory.manager import MemoryManager
from copy import deepcopy
from typing import Any
from agent_engineer.agent.loop_guard import(
    LoopDetector,
    LoopPolicy
)
from agent_engineer.resilience.retry import (
    RetryExecutor,
    RetryPolicy,
)
from agent_engineer.llm.validation import (
    validate_llm_response,
)
from agent_engineer.security.guardrails import (
    SecurityGuard,
)
from agent_engineer.security.policy import (
    SecurityContext,
)

from agent_engineer.observability.trace import (
    Trace,
    Tracer,
)

from contextlib import nullcontext

from agent_engineer.observability.event import Event

from agent_engineer.tools.types import (
    ToolCall,
    ToolResult,
)

from agent_engineer.tools.executor import (
    ToolExecutor,
)

from contextlib import AbstractContextManager

from agent_engineer.observability.trace import Span

from agent_engineer.optimization.budget import BudgetManager

class AgentLoop:
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
        budget: BudgetManager | None = None,
        max_steps: int = 10,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        self.llm = llm
        self.tool_executor = tool_executor
        self.planner = planner
        self.memory_manager = memory_manager
        self.budget = budget
        self.max_steps = max_steps

        self.retry_executor = (
            RetryExecutor(retry_policy)
            if retry_policy is not None
            else None
        )
        self.loop_policy = loop_policy
        self.security_guard = security_guard
        self.tracer = tracer

    #===================================================
    # MAIN AGENT LOOP
    #===================================================

    def run(
        self, 
        state: AgentState, 
        goal: str | None = None,
        security_context: SecurityContext | None = None
    ) -> AgentState:

        goal = goal or ""

        security_context = (
            security_context
            if security_context is not None
            else SecurityContext()
        )

        # Runtime state must not leak between Agent runs
        loop_detector = LoopDetector(
            self.loop_policy
        ) if self.loop_policy is not None else None

        # PLAN
        self.plan(
            state=state,
            goal=goal,
        )

        while not self.should_stop(state):

            # REASON
            response = self.reason(
                state=state,
                goal=goal,
            )

            # FINAL ANSWER
            if response.is_final:
                self._handle_final_response(
                    state=state,
                    response=response,
                )
                continue

            state.add_message(
                Message(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            state.trajectory.add(
                AgentStep(
                    step_number=state.step_count,
                    step_type=StepType.LLM,
                    data=response,
                )
            )

            observations: list[Any] = []

            # SELECT ACTION
            tool_calls = self.select_tool(
                response=response,
            )

            if (
                tool_calls
                and self.tool_executor is None
            ):
                raise AgentError(
                    "Tool calls were generated, but no ToolExecutor is configured."
                )

            # ACT
            for tool_call in tool_calls:

                result = self.execute_tool(
                    tool_call=tool_call,
                    security_context=security_context,
                    loop_detector=loop_detector,
                )

                observations.append(result)

                # Observe
                self.observe(
                    state=state,
                    tool_call=tool_call,
                    result=result,
                )
            # Replan if necessary
            if (
                observations
                and self.planner is not None
                and state.plan is not None
            ):
                with self._span(
                    "planner.update"
                ):
                    self._update_plan(
                        goal=goal,
                        state=state,
                        observations=observations,
                    )
        
        return state

    # ==================================================
    # 1. PLAN
    # ==================================================

    def plan(
        self,
        state: AgentState,
        goal: str,
    ) -> None:

        if self.planner is None:
            return

        if state.plan is not None:
            return

        with self._span("planner"):

            state.plan = (
                self.planner.create_plan(
                    goal
                )
            )

            state.plan.start()

        state.trajectory.add(
            AgentStep(
                step_number=state.step_count,
                step_type=StepType.PLAN,
                data=deepcopy(state.plan)
            )
        )

    #==================================================
    # 2. REASON
    #==================================================
    
    def reason(
        self,
        state: AgentState,
        goal: str,
    ) -> LLMResponse:

        if (
            state.step_count
            >= self.max_steps
        ):
            raise MaxStepsExceededError(
                f"Maximum number of steps ({self.max_steps}) exceeded."
            )

        if self.budget is not None:
            self.budget.record_step()

        request = LLMRequest(
            messages = self._build_messages(
                state=state,
                goal=goal,
            ),
        )

        def generate() -> LLMResponse:
            return self.llm.generate(
                request=request,
            )

        with self._span("llm") as span:

            def on_retry(
                error: AgentError,
                retry_number: int,
                delay: float,
            ) -> None:

                if span is None:
                    return

                span.record_retry()

                if self.tracer is not None:
                    span.add_event(
                        Event(
                            name="retry",
                            timestamp=(
                                self.tracer.clock()
                            ),
                            attributes={
                                "retry_number": retry_number,
                                "delay": delay,
                                "error":
                                    type(error).__name__,
                            },
                        )
                    )

            if self.retry_executor is None:
                response = generate()

            else:
                response = (
                    self.retry_executor.execute(
                        generate,
                        on_retry=on_retry,
                    )
                )

            validate_llm_response(
                response=response,
            )

            if self.budget is not None:
                self.budget.record_tokens(
                    response.usage.total_tokens
                )

            if span is not None:

                span.add_usage(
                    input_tokens=(
                        response.usage.input_tokens
                    ),
                    output_tokens=(
                        response.usage.output_tokens
                    ),
                )

                span.attributes[
                    "model"
                ] = response.model

        state.increment_step()

        return response

    #==================================================
    # 3. SELECT TOOL
    #==================================================
    def select_tool(
        self,
        response: LLMResponse,
    ) -> list[ToolCall]:
        """
        The LLM has already selected the tools

        This method makes the Agent primitive explicit
        without duplicating tool routing logic
        """
        return response.tool_calls

    #=================================================
    # 4. EXECUTE TOOL
    #=================================================

    def execute_tool(
        self,
        tool_call: ToolCall,
        security_context: SecurityContext,
        loop_detector: LoopDetector | None = None,
    ) -> ToolResult:

        if self.tool_executor is None:
            raise AgentError(
                "Agent has no ToolExecutor"
            )

        with self._span(
            f"tool.{tool_call.name}"
        ) as span:

            if span is not None:

                span.record_tool_call()

                span.attributes[
                    "tool_name"
                ] = tool_call.name

            # Loop protection
            if loop_detector is not None:
                loop_detector.record_tool_call(
                    call=tool_call,
                )

            # Security boundary
            if self.security_guard is not None:
                self.security_guard.check(
                    call=tool_call,
                    context=security_context,
                )

            return self.tool_executor.execute(
                call=tool_call,
            )

    #=================================================
    # 5. OBSERVE
    #=================================================
    
    def observe(
        self,
        state: AgentState,
        tool_call: ToolCall,
        result: ToolResult,
    ) -> None:

        state.trajectory.add(
            AgentStep(
                step_number=state.step_count,
                step_type=StepType.TOOL_CALL,
                data=tool_call,
            )
        )

        state.trajectory.add(
            AgentStep(
                step_number=state.step_count,
                step_type=StepType.OBSERVATION,
                data=result,
            )
        )

        state.add_message(
            Message(
                role="tool",
                content=(
                    self._format_tool_output(
                        result.output
                    )
                ),
                tool_calls=[],
                tool_call_id=tool_call.id,
                name=tool_call.name,
            )
        )

    #=================================================
    # 6. SHOULD STOP
    #=================================================

    def should_stop(
        self,
        state: AgentState,
    ) -> bool:
        return state.finished

    #=================================================
    # FINAL RESPONSE
    #=================================================

    def _handle_final_response(
        self,
        state: AgentState,
        response: LLMResponse,
    ) -> None:

        answer = response.content or ""

        state.add_message(
            Message(
                role="assistant",
                content=answer,
                tool_calls=[],
            )
        )

        state.trajectory.add(
            AgentStep(
                step_number=state.step_count,
                step_type=StepType.FINAL,
                data=answer,
            )
        )

        state.finish(
            answer=answer
        )   

    #=================================================
    # CONTEXT BUILDING
    #=================================================

    def _build_messages(
        self,
        state: AgentState,
        goal: str,
    ) -> list[Message]:

        context_messages: list[Message] = []

        # Current plan
        if state.plan is not None:

            context_messages.append(
                Message(
                    role="system",
                    content=f"Current execution plan: {state.plan.to_text()}",
                    tool_calls=[],
                )
            )

        # Relevant memories
        if self.memory_manager is not None:

            memories = (
                self.memory_manager.retrieve_relevant(
                    query=goal,
                    limit=5,
                )
            )

            if memories:
                memory_text = "\n".join(
                    f"- {item.content}" for item in memories
                )

                context_messages.append(
                    Message(
                        role="system",
                        content=f"Relevant memories:\n{memory_text}",
                        tool_calls=[],
                    )
                )

        return [ 
            *context_messages,
            *state.messages,
        ]

    #=================================================
    # REPLANNING
    #=================================================
    def _update_plan(
        self,
        goal: str,
        state: AgentState,
        observations: list[Any],
    ) -> None:

        if self.planner is None:
            return

        if state.plan is None:
            return

        for observation in observations:

            should_replan = self.planner.should_replan(
                state.plan,
                observation,
            )

            if not should_replan:
                continue

            if (
                state.replan_count >= self.planner.max_replans
            ):
                return

            old_plan = state.plan
            old_plan.invalidate()

            new_plan = self.planner.replan(
                goal=goal,
                plan=old_plan,
                observation=observation,
            )

            new_plan.start()

            state.plan = new_plan
            state.replan_count += 1

            state.trajectory.add(
                AgentStep(
                    step_number=state.step_count,
                    step_type=StepType.REPLAN,
                    data=deepcopy(new_plan)
                )
            )

            return

        state.plan.complete_current_step()

    #=================================================
    #  OBSERVABILITY
    #=================================================

    def _span(
        self,
        name: str,
    ) -> AbstractContextManager[Span | None]:

        if self.tracer is None:
            return nullcontext(None)

        return self.tracer.span(name)

    #=================================================
    # TOOL OUTPUT
    #=================================================

    @staticmethod
    def _format_tool_output(output: object) -> str:

        if isinstance(output, (list, tuple)):
            return "\n".join(str(item) for item in output)
        return str(output)