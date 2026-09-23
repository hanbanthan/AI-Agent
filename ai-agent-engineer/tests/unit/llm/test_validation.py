import pytest

from agent_engineer.llm.errors import (
    LLMInvalidResponseError,
)
from agent_engineer.llm.types import (
    LLMResponse,
)
from agent_engineer.llm.validation import (
    validate_llm_response,
)


def test_empty_llm_response_is_invalid() -> None:

    response = LLMResponse(
        content=None,
        model="mock-model",
        tool_calls=[],
    )

    with pytest.raises(
        LLMInvalidResponseError
    ):
        validate_llm_response(response)