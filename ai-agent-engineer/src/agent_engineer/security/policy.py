from dataclasses import dataclass, field
from enum import Enum

from agent_engineer.security.errors import (
    ConfirmationRequiredError,
    DataFlowViolationError,
    PermissionDeniedError,
)

from agent_engineer.security.permissions import (
    Permission,
    ToolPermission,
)

class InstructionTrust(str, Enum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"

class DataSensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"

@dataclass(frozen=True)
class SecurityContext:
    instruction_trust: InstructionTrust = (
        InstructionTrust.TRUSTED
    )

    confirmed_permissions: frozenset[
        Permission
    ] = field(
        default_factory=frozenset
    )

    data_sensitivity: DataSensitivity = (
        DataSensitivity.PUBLIC
    )

@dataclass(frozen=True)
class SecurityPolicy:
    allowed_permissions: frozenset[
        Permission
    ] = field(
        default_factory=lambda: frozenset(
            {
                Permission.READ,
            }
        )
    )

    allow_sensitive_external_flow: bool = False

    def check(
        self,
        tool_permission: ToolPermission,
        context: SecurityContext,
    ) -> None:

        permission = (
            tool_permission.permission
        )

        # Deny permission not explicitly allowed
        if permission not in self.allowed_permissions:
            raise PermissionDeniedError(
                f"Permission {permission} is not allowed for tool {tool_permission.tool_name}."
            )

        # Untrusted retrieved/web/tool data cannot authorize state-changing operations
        if (
            context.instruction_trust
            == InstructionTrust.UNTRUSTED
            and permission 
            in {
                Permission.WRITE,
                Permission.SENSITIVE,
            }
        ):
            raise PermissionDeniedError(
                f"Untrusted instruction cannot authorize {permission} permission for tool {tool_permission.tool_name}."
            )

        # Sensitive operations need explicit confirmation
        if (
            permission == Permission.SENSITIVE
            and permission not in context.confirmed_permissions
        ):
            raise ConfirmationRequiredError(
                f"Sensitive operation {permission} for tool {tool_permission.tool_name} requires explicit confirmation."
            )

        # Stop sensitive information leaving through an external tool
        if (
            tool_permission.external
            and context.data_sensitivity
            == DataSensitivity.SENSITIVE
            and not self.allow_sensitive_external_flow
        ): 
            raise DataFlowViolationError(
                f"Sensitive data cannot flow to external tool {tool_permission.tool_name}."
            )

        