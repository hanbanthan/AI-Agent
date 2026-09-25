from dataclasses import dataclass
from enum import Enum

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    SENSITIVE = "sensitive"

@dataclass(frozen=True)
class ToolPermission:
    tool_name: str
    permission: Permission
    external: bool = False

class ToolPermissionRegistry:

    def __init__(self) -> None:
        self._permissions: dict[
            str,
            ToolPermission,
        ] = {}

    def register(
        self,
        permission: ToolPermission
    ) -> None:
        self._permissions[permission.tool_name] = permission

    def get(
        self,
        tool_name: str
    ) -> ToolPermission | None:
        return self._permissions.get(tool_name)

