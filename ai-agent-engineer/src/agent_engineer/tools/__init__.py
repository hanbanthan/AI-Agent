from agent_engineer.tools.base import Tool
from agent_engineer.tools.executor import ToolExecutor
from agent_engineer.tools.registry import ToolRegistry
from agent_engineer.tools.types import (
	ToolCall,
	ToolParameter,
	ToolResult,
	ToolSchema,
)

def __getattr__(name: str):
	if name == "RAGTool":
		from agent_engineer.rag.tool import RAGTool

		return RAGTool
	raise AttributeError(name)


__all__ = [
	"RAGTool",
	"Tool",
	"ToolCall",
	"ToolExecutor",
	"ToolParameter",
	"ToolRegistry",
	"ToolResult",
	"ToolSchema",
]
