from abc import ABC, abstractmethod
from typing import Any

from agent_engineer.tools.types import ToolSchema

class Tool(ABC):
    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        """Return the schema of the tool."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with the given arguments."""
        raise NotImplementedError