import pytest

from agent_engineer.agent.errors import (
    RepeatedActionError,
)
from agent_engineer.agent.loop_guard import (
    LoopDetector,
    LoopPolicy,
)
from agent_engineer.tools.types import ToolCall


def test_repeated_tool_call_detected() -> None:

    detector = LoopDetector(
        LoopPolicy(
            max_repeated_actions=2
        )
    )

    call = ToolCall(
        name="search",
        arguments={
            "query": "Bitcoin",
        },
    )

    detector.record_tool_call(call)
    detector.record_tool_call(call)

    with pytest.raises(
        RepeatedActionError
    ):
        detector.record_tool_call(call)

def test_different_tool_calls_are_not_loop() -> None:

    detector = LoopDetector(
        LoopPolicy(
            max_repeated_actions=2
        )
    )

    detector.record_tool_call(
        ToolCall(
            name="search",
            arguments={"query": "Bitcoin"},
        )
    )

    detector.record_tool_call(
        ToolCall(
            name="search",
            arguments={"query": "Ethereum"},
        )
    )

    detector.record_tool_call(
        ToolCall(
            name="search",
            arguments={"query": "Solana"},
        )
    )