import pytest

from agent_engineer.security.errors import (
    SecurityValidationError,
)
from agent_engineer.security.validation import (
    InputValidator,
)
from agent_engineer.tools.types import (
    ToolCall,
)

from agent_engineer.security.permissions import (
    Permission,
    ToolPermission,
)

from agent_engineer.security.policy import (
    SecurityContext,
    SecurityPolicy,
)

from agent_engineer.security.errors import (
    PermissionDeniedError,
    DataFlowViolationError,
    SecurityValidationError
)

from agent_engineer.security.policy import (
    InstructionTrust,
    DataSensitivity,
)

def test_malicious_tool_arguments() -> None:

    validator = InputValidator()

    call = ToolCall(
        name="open-url",
        arguments={
            "url": "javascript:alert(1)",
        },
    )

    with pytest.raises(SecurityValidationError):
        validator.validate(call)

def test_null_byte_is_rejected() -> None:

    validator = InputValidator()

    call = ToolCall(
        name="read_file",
        arguments={
            "path": "report.txt\x00.exe",
        },
    )

    with pytest.raises(SecurityValidationError):
        validator.validate(call)

def test_untrusted_document_cannot_authorize_write() -> None:

    policy = SecurityPolicy(
        allowed_permissions=frozenset(
            {
                Permission.READ,
                Permission.WRITE,
            }
        )
    )

    permission = ToolPermission(
        tool_name="delete_file",
        permission=Permission.WRITE,
    )

    context = SecurityContext(
        instruction_trust=(
            InstructionTrust.UNTRUSTED  
        )
    )

    with pytest.raises(PermissionDeniedError):
        policy.check(
            tool_permission=permission,
            context=context,
        )

def test_instruction_can_authorize_write() -> None:

    policy = SecurityPolicy(
        allowed_permissions=frozenset(
            {
                Permission.READ,
                Permission.WRITE,
            }
        )
    )

    permission = ToolPermission(
        tool_name="save_file",
        permission=Permission.WRITE,
    )

    context = SecurityContext(
        instruction_trust=(
            InstructionTrust.TRUSTED  
        )
    )

    policy.check(
        tool_permission=permission,
        context=context,
    )

def test_sensitive_data_cannot_flow_external() -> None:

    policy = SecurityPolicy(
        allowed_permissions=frozenset(
            {
                Permission.READ,
            }
        )
    )

    permission = ToolPermission(
        tool_name="external_search",
        permission=Permission.READ,
        external=True,
    )

    context = SecurityContext(
        data_sensitivity=(
            DataSensitivity.SENSITIVE
        )
    )

    with pytest.raises(
        DataFlowViolationError
    ):
        policy.check(
            tool_permission=permission,
            context=context,
        )