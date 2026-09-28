from agent_engineer.llm.mock import (
    MockLLM,
)
from agent_engineer.llm.types import (
    LLMResponse,
    Usage,
)

from tests.unit.llm.provider_contract import (
    assert_provider_contract,
)

def test_mock_llm_provider_contract() -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Hello!",
                model="mock-model",
                usage=Usage(
                    input_tokens=5,
                    output_tokens=2,
                ),
                latency_ms=1.0,
                raw_response={
                    "mock": True
                },
            )
        ]
    )

    response = (
        assert_provider_contract(
            llm
        )
    )

    assert (
        response.content
        == "Hello!"
    )

    assert (
        response.raw_response
        == {"mock": True}
    )