from agent_engineer.llm.errors import (
    LLMInvalidResponseError,
)

from agent_engineer.llm.types import LLMResponse

def validate_llm_response(
    response: LLMResponse,
) -> None:

    if (
        response.content is None
        and not response.tool_calls
    ):
        raise LLMInvalidResponseError(
            "LLM response must contain either content or tool calls."
        )

    for tool_call in response.tool_calls:

        if not tool_call.name.strip():
            raise LLMInvalidResponseError(
                "Tool call name cannot be empty."
            )

        if not isinstance(
            tool_call.arguments,
            dict,
        ):
            raise LLMInvalidResponseError(
                "Tool call arguments must be a dictionary."
            )
        