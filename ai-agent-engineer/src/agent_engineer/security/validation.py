'''
Security validatio focus on obviously dangerous malformed input rather than duplicate the tool schema validator
'''
from typing import Any

from agent_engineer.security.errors import (
    SecurityValidationError,
)

from agent_engineer.tools.types import ToolCall

class InputValidator:

    def __init__(
        self,
        max_string_length: int = 10_000,
    ) -> None:

        if max_string_length <= 0:
            raise ValueError(
                "max_string_length must be a positive integer"
            )

        self.max_string_length = max_string_length

    def validate(
        self,
        call: ToolCall,
    ) -> None:

        if not isinstance(call, ToolCall):
            raise SecurityValidationError(
                "Tool call must be a ToolCall"
            )

        for name, value in call.arguments.items():
            self._validate_value(
                value,
                path=name,
            )

    def _validate_value(
        self,
        value: Any,
        path: str,
    ) -> None:

        if isinstance(value, str):
            self._validate_string(
                value,
                path=path,
            )

        elif isinstance(value, dict):
            for key, nested in value.items():
                self._validate_value(
                    nested,
                    f"{path}.{key}",
                )

        elif isinstance(value, list):
            for index, nested in enumerate(
                value
            ):
                self._validate_value(
                    nested,
                    f"{path}[{index}]",
                )

    def _validate_string(
        self,
        value: str,
        path: str,
    ) -> None:

        if len(value) > self.max_string_length:
            raise SecurityValidationError(
                f"String at {path} exceeds maximum length of {self.max_string_length}"
            )

        if "\x00" in value:
            raise SecurityValidationError(
                f"String at {path} contains null byte"
            )

        normalized = value.strip().lower()

        if normalized.startswith(
            "javascript:"
        ):
            raise SecurityValidationError(
                f"Argument '{path}' contains potentially dangerous JavaScript code" 
            )   
        