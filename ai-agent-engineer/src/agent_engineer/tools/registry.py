from agent_engineer.tools.base import Tool
from agent_engineer.tools.errors import (
    DuplicateToolError,
    ToolNotFoundError,
)

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = tool.schema.name

        if name in self._tools:
            raise DuplicateToolError(f"Tool '{name}' is already registered.")

        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.") from exc

    def list_tools(self) -> list[str]:
        return list(self._tools.values())

    def __contains__(self, name: str) -> bool:
        return name in self._tools
        