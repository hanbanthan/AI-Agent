import pytest


from agent_engineer.security.errors import (
    PermissionDeniedError,
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
    ConfirmationRequiredError,
)

def test_unauthorized_write() -> None:

    policy = SecurityPolicy()

    permission = ToolPermission(
        tool_name="save_file",
        permission=Permission.WRITE,
    )

    with pytest.raises(PermissionDeniedError):
        policy.check(
            tool_permission=permission,
            context=SecurityContext(),
        )

def test_sensitive_operation_requires_confirmation() -> None:

    policy = SecurityPolicy(
        allowed_permissions=frozenset(
            {
                Permission.READ,
                Permission.SENSITIVE,
            }
        )
    )

    permission = ToolPermission(
        tool_name="send_email",
        permission=Permission.SENSITIVE,
    )

    with pytest.raises(ConfirmationRequiredError):
        policy.check(
            tool_permission=permission,
            context=SecurityContext(),
        )

def test_sensitive_operation_with_confirmation() -> None:

    policy = SecurityPolicy(
        allowed_permissions=frozenset(
            {
                Permission.READ,
                Permission.SENSITIVE,
            }
        )
    )

    permission = ToolPermission(
        tool_name="send_email",
        permission=Permission.SENSITIVE,
    )

    context = SecurityContext(
        confirmed_permissions=frozenset(
            {
                Permission.SENSITIVE,
            }
        )
    )

    policy.check(
        permission,
        context,
    )