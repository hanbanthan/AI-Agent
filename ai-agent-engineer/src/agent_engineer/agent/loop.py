from agent_engineer.agent.errors import MaxStepsExceededError
from agent_engineer.agent.state import AgentState
from agent_engineer.agent.trajectory import AgentStep, StepType
from agent_engineer.llm.base import LLM
from agent_engineer.llm.types import LLMRequest, Message
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.planning.base import Planner
from agent_engineer.memory.manager import MemoryManager
from copy import deepcopy
from typing import Any

class AgentLoop:
    def __init__(
        self,
        llm: LLM,
        tool_executor: ToolExecutor | None = None,
        planner: Planner | None = None,
        memory_manager: MemoryManager | None = None,
        max_steps: int = 10,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        self.llm = llm
        self.tool_executor = tool_executor
        self.planner = planner
        self.memory_manager = memory_manager
        self.max_steps = max_steps

    def run(self, state: AgentState, goal: str | None = None) -> AgentState:
        if self.planner is not None and state.plan is None:
            state.plan = self.planner.create_plan(goal or "")
            state.plan.start()
            state.trajectory.add(
                AgentStep(
                    step_number=state.step_count,
                    step_type=StepType.PLAN,
                    data=deepcopy(state.plan),
                )
            )

        while not state.finished:
            if state.step_count >= self.max_steps:
                raise MaxStepsExceededError(
                    f"Agent exceeded the maximum number of steps: {self.max_steps}"
                )

            request = LLMRequest(
                messages=self._build_messages(state, goal or ""),
            )

            response = self.llm.generate(request)

            state.increment_step()

            if response.is_final:
                answer = response.content or ""

                state.add_message(
                    Message(
                        role="assistant",
                        content=answer,
                    )
                )

                state.trajectory.add(
                    AgentStep(
                        step_number=state.step_count,
                        step_type=StepType.FINAL,
                        data=answer,
                    )
                )   

                state.finish(answer=answer)

                continue

            if self.tool_executor is None:
                continue

            state.trajectory.add(
                AgentStep(
                    step_number=state.step_count,
                    step_type=StepType.LLM,
                    data=response,
                )
            )

            observations = []
            for tool_call in response.tool_calls:

                state.trajectory.add(
                    AgentStep(
                        step_number=state.step_count,
                        step_type=StepType.TOOL_CALL,
                        data=tool_call,
                    )
                )

                result = self.tool_executor.execute(tool_call)  
                observations.append(result)

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
                        content=self._format_tool_output(result.output),
                        tool_call_id=tool_call.id,
                    )
                )

            self._update_plan(goal or "", state, observations)

        return state

    @staticmethod
    def _format_tool_output(output: object) -> str:
        if isinstance(output, (list, tuple)):
            return "\n".join(str(item) for item in output)
        return str(output)

    def _build_messages(
            self,
            state: AgentState,
            goal: str,
    ) -> list[Message]:

        context_messages: list[Message] = []

        if state.plan is not None:
            context_messages.append(
                Message(
                    role="system",
                    content=f"Current execution plan: {state.plan.to_text()}",
                )
            )
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
                    )
                )

        return [ 
            *context_messages,
            *state.messages,
        ]

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



    