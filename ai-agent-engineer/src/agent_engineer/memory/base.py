import re

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from agent_engineer.memory.errors import (
    DuplicateMemoryError,
    MemoryNotFoundError,
)

class MemoryKind(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

@dataclass(frozen=True)
class MemoryItem:
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())

def memory_score(
        content,
        query: str,
) -> float:
    query_tokens = set(
        re.findall(r"\w+", query.lower())
    )

    content_tokens = set(
        re.findall(r"\w+", content.lower())
    )

    if not query_tokens:
        return 0.0

    overlap = len(
        query_tokens & content_tokens
    )

    return overlap / len(query_tokens)

class Memory(ABC):

    @abstractmethod
    def store(
        self,
        item: MemoryItem,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[MemoryItem]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        item_id: str,
        content: str,
    ) -> MemoryItem:
        raise NotImplementedError

class InMemoryMemory(Memory):

    def __init__(self):
        self._items: dict[str, MemoryItem] = {}

    def _is_duplicate(
        self,
        item: MemoryItem,
        ignore_id: str | None = None,
    ) -> bool:

        normalized = normalize_text(item.content)

        for existing in self._items.values():
            if existing.id == ignore_id:
                continue

            if (
                normalize_text(existing.content) == normalized
            ):
                return True

        return False

    def store(
        self,
        item: MemoryItem,
    ) -> bool:

        if item.id in self._items:
            return False

        if self._is_duplicate(item):
            return False

        self._items[item.id] = item

        return True

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[MemoryItem]:

        if limit <= 0:
            return []

        items = list(self._items.values())

        if not query.strip():
            return items[-limit:]

        scored = [
            (
                memory_score(
                    item.content,
                    query,
                ),
                item,
            )
            for item in items
        ]

        scored = [
            pair 
            for pair in scored
            if pair[0] > 0
        ]

        scored.sort(
            key=lambda pair: pair[0],
            reverse=True,
        )

        return [
            item
            for _, item in scored[:limit]
        ]

    def get(
        self,
        item_id: str,
    ) -> MemoryItem:

        try:
            return self._items[item_id]

        except KeyError as exc:
            raise MemoryNotFoundError(
                f"Memory item with ID '{item_id}' not found."
            ) from exc

    def update(
        self,
        item_id: str,
        content: str,
    ) -> MemoryItem:

        old_item = self.get(item_id)

        new_item = replace(
            old_item,
            content=content,
        )

        if self._is_duplicate(new_item, ignore_id=item_id):
            raise DuplicateMemoryError(
                f"Duplicate memory item with content '{content}' exists."
            )

        self._items[item_id] = new_item

        return new_item

    def __len__(self) -> int:
        return len(self._items)

    

    