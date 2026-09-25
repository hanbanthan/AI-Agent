from agent_engineer.security.errors import (
    PermissionDeniedError,
)
from agent_engineer.security.permissions import (
    ToolPermissionRegistry,
)
from agent_engineer.security.policy import (
    SecurityContext,
    SecurityPolicy,
)
from agent_engineer.security.validation import (
    InputValidator,
)
from agent_engineer.tools.types import (
    ToolCall,
)

class SecurityGuard:

    def __init__(
        self,
        permissions: ToolPermissionRegistry,
        policy: SecurityPolicy,
        validator: InputValidator | None = None
    ) -> None:

        self.permissions = permissions
        self.policy = policy

        self.validator = (
            validator
            if validator is not None
            else InputValidator()
        )

    def check(
        self,
        call: ToolCall,
        context: SecurityContext,
    ) -> None:

        # Permission check
        tool_permission = (
            self.permissions.get(call.name)
        )

        if tool_permission is None:
            raise PermissionDeniedError(
                f"Tool '{call.name}' is not registered in the permission registry"
            )

        # INput validation
        self.validator.validate(call)

        # Security policy check
        self.policy.check(
            tool_permission,
            context,
        )
        