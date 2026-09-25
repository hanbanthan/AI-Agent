from typing import Any

from agent_engineer.tools.errors import (
    ToolExecutionError,
    ToolValidationError,
)

from agent_engineer.tools.registry import ToolRegistry
from agent_engineer.tools.types import (
    ToolCall,
    ToolParameter,
    ToolResult,
)

from concurrent.futures import (
    ThreadPoolExecutor,
)

from agent_engineer.tools.types import ToolCall, ToolResult


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, call: ToolCall) -> ToolResult:
        tool = self.registry.get(call.name)

        self._validate_arguments(
            parameters=tool.schema.parameters,
            arguments=call.arguments,
        )

        try:
            output = tool.execute(**call.arguments)

            return ToolResult(
                tool_name=call.name,
                success=True,
                output=output,
                call_id=call.id,
            )
        except Exception as exc:
            raise ToolExecutionError(
                f"Error executing tool '{call.name}': {exc}"
            ) from exc

    '''
    1. Required argument missing?

    2. Unknown argument supplied?

    3. Argument has wrong Python type?
    '''
    def _validate_arguments(
        self,
        parameters: list[ToolParameter],
        arguments: dict[str, Any],
    ) -> None:
        parameter_map = {
            parameter.name: parameter
            for parameter in parameters
        }

        for parameter in parameters:
            if (
                parameter.required
                and parameter.name not in arguments
            ):
                raise ToolValidationError(
                    f"Missing required argument: '{parameter.name}'"
            )

        for name, value in arguments.items():
            if name not in parameter_map:
                raise ToolValidationError(
                    f"Unexpected argument: '{name}'"
                )

            expected_type = parameter_map[name].type
            if not isinstance(value, expected_type):
                raise ToolValidationError(
                    f"Argument '{name}' must be of type "
                    f"'{expected_type.__name__}', got "
                    f"'{type(value).__name__}' instead."
                )

def execute_many(
    self,
    calls: list[ToolCall],
    max_workers: int = 4,
) -> list[ToolResult]:

    if not calls:
        return []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = [
            executor.submit(self.execute, call)
            for call in calls
        ]

        return [
            future.result()
            for future in futures
        ]
    