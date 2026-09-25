from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Event:
    name: str
    timestamp: float
    attributes: dict[str, Any] = field(default_factory=dict)

