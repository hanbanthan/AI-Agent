from dataclasses import dataclass
from enum import Enum

from agent_engineer.errors import AgentError
from agent_engineer.llm.errors import LLMError
from agent_engineer.memory.errors import (
    MemorySystemError,
)
from agent_engineer.planning.errors import PlanningError
from agent_engineer.rag.errors import RetrievalError
from agent_engineer.tools.errors import ToolError

class FailureCategory(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    PLANNING = "planning"
    RETRIEVAL = "retrieval"
    MEMORY = "memory"
    LOOP = "loop"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class FailureInfo:
    category: FailureCategory
    retryable: bool
    error_type: str
    message: str

class FailureClassifier:

    def classify(
        self,
        error: Exception,
    ) -> FailureInfo:

        category = self._category(error)

        retryable = (
            error.retryable
            if isinstance(error, AgentError)
            else False
        )

        return FailureInfo(
            category=category,
            retryable=retryable,
            error_type=type(error).__name__,
            message=str(error),
        )

    def _category(
        self,
        error: Exception,
    ) -> FailureCategory:
        if isinstance(error, LLMError):
            return FailureCategory.LLM
        elif isinstance(error, ToolError):
            return FailureCategory.TOOL
        elif isinstance(error, PlanningError):
            return FailureCategory.PLANNING
        elif isinstance(error, RetrievalError):
            return FailureCategory.RETRIEVAL
        elif isinstance(error, MemorySystemError):
            return FailureCategory.MEMORY
        else:
            return FailureCategory.UNKNOWN

    