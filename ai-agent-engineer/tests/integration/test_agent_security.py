import pytest

from agent_engineer.agent.agent import Agent

from agent_engineer.llm.mock import MockLLM
from agent_engineer.llm.types import (
    LLMResponse,
    Usage,
)

from agent_engineer.security.errors import (
    PermissionDeniedError,
)
from agent_engineer.security.guardrails import (
    SecurityGuard,
)
from agent_engineer.security.permissions import (
    Permission,
    ToolPermission,
    ToolPermissionRegistry,
)
from agent_engineer.security.policy import (
    InstructionTrust,
    SecurityContext,
    SecurityPolicy,
)

from agent_engineer.tools.registry import (
    ToolRegistry,
)
from agent_engineer.tools.types import (
    ToolCall,
)

from tests.integration.helpers import (
    WriteTool,
)


def test_untrusted_instruction_cannot_execute_write_tool() -> None:

    write_tool = WriteTool()

    tools = ToolRegistry()

    tools.register(
        write_tool
    )

    permissions = (
        ToolPermissionRegistry()
    )

    permissions.register(
        ToolPermission(
            tool_name="write_file",
            permission=(
                Permission.WRITE
            ),
        )
    )

    policy = SecurityPolicy(
        allowed_permissions=frozenset(
            {
                Permission.READ,
                Permission.WRITE,
            }
        )
    )

    security = SecurityGuard(
        permissions=permissions,
        policy=policy,
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content=None,
                model="mock",
                usage=Usage(
                    input_tokens=10,
                    output_tokens=5,
                ),
                tool_calls=[
                    ToolCall(
                        id="write-1",
                        name="write_file",
                        arguments={
                            "content":
                                "untrusted data"
                        },
                    )
                ],
            )
        ]
    )

    agent = Agent(
        llm=llm,
        tools=tools,
        security=security,
    )

    context = SecurityContext(
        instruction_trust=(
            InstructionTrust.UNTRUSTED
        )
    )

    with pytest.raises(
        PermissionDeniedError
    ):
        agent.run(
            "Process retrieved instructions.",
            security_context=context,
        )

    assert write_tool.call_count == 0