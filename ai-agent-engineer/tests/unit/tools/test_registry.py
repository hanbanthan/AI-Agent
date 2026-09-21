import pytest

from agent_engineer.tools.errors import (
    DuplicateToolError,
    ToolNotFoundError,
)
from agent_engineer.tools.registry import ToolRegistry

def test_register_tool(search_tool) -> None:
    registry = ToolRegistry()

    registry.register(search_tool)

    assert "search" in registry
    assert registry.get("search") is search_tool

def test_duplicate_tool(search_tool) -> None:
    registry = ToolRegistry()

    registry.register(search_tool)

    with pytest.raises(DuplicateToolError):
        registry.register(search_tool)

def test_unknown_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(ToolNotFoundError):
        registry.get("unknown")