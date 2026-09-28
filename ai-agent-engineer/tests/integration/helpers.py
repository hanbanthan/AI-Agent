from agent_engineer.tools.base import Tool
from agent_engineer.tools.types import (
    ToolParameter,
    ToolSchema,
)

class AddTool(Tool):

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="add",
            description="Add two integers.",
            parameters=[
                ToolParameter(
                    name="a",
                    type=int,
                    description="First number",
                ),
                ToolParameter(
                    name="b",
                    type=int,
                    description="Second number",
                ),
            ],
        )

    def execute(
        self,
        **kwargs,
    ) -> int:
        return (
            kwargs["a"]
            + kwargs["b"]
        )

class MultiplyTool(Tool):

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="multiply",
            description="Multiply two integers.",
            parameters=[
                ToolParameter(
                    name="a",
                    type=int,
                    description="First number",
                ),
                ToolParameter(
                    name="b",
                    type=int,
                    description="Second number",
                ),
            ],
        )

    def execute(
        self,
        **kwargs,
    ) -> int:
        return (
            kwargs["a"]
            * kwargs["b"]
        )

class FailingTool(Tool):

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="failing_tool",
            description="A tool that always fails.",
            parameters=[],
        )

    def execute(
        self,
        **kwargs,
    ) -> str:
        raise RuntimeError(
            "Simulated tool failure"
        )

class WriteTool(Tool):

    def __init__(self) -> None:
        self.call_count = 0

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="write_file",
            description="Write data to a file.",
            parameters=[
                ToolParameter(
                    name="content",
                    type=str,
                    description="File content",
                ),
            ],
        )

    def execute(
        self,
        **kwargs,
    ) -> str:
        self.call_count += 1
        return "written"
    