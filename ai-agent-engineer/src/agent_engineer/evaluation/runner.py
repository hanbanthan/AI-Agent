from collections.abc import Callable
from time import perf_counter
from typing import Protocol

from agent_engineer.agent.agent import (
    AgentResult,
)
from agent_engineer.evaluation.dataset import (
    EvaluationDataset,
)
from agent_engineer.evaluation.result import (
    EvaluationResult,
)
from agent_engineer.evaluation.trajectory import (
    Evaluator,
)

class RunnableAgent(Protocol):

    def run(
        self,
        user_input: str,
    ) -> AgentResult:
        ...

class EvaluationRunner:

    def __init__(
        self,
        agent_factory: Callable[
            [], RunnableAgent
        ],
        evaluator: Evaluator,
    ) -> None:
        self.agent_factory = agent_factory
        self.evaluator = evaluator

    def run(
        self,
        dataset: EvaluationDataset,
    ) -> list[EvaluationResult]:

        results: list[EvaluationResult] = []

        for case in dataset.cases:

            agent = self.agent_factory()

            agent_result: AgentResult | None = None
            error: Exception | None = None

            start = perf_counter()

            try:
                agent_result = agent.run(
                    user_input=case.input,
                )

            except Exception as e:
                error = e

            latency_ms = (perf_counter() - start) * 1000

            evaluation = (
                self.evaluator.evaluate(
                    case=case,
                    result=agent_result,
                    error=error,
                    latency_ms=latency_ms,
                )
            )

            results.append(evaluation)

        return results