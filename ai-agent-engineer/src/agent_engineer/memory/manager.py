import hashlib

from agent_engineer.llm.types import Message

from agent_engineer.memory.base import (
    Memory,
    MemoryItem,
    MemoryKind,
    memory_score,
    normalize_text,
)

from agent_engineer.memory.episodic import (
    EpisodicMemory,
)
from agent_engineer.memory.errors import (
    MemoryRetrievalError,
)
from agent_engineer.memory.policy import (
    MemoryPolicy,
)
from agent_engineer.memory.semantic import (
    SemanticMemory,
)
from agent_engineer.memory.working import (
    WorkingMemory,
)

class MemoryManager:

    def __init__(
        self,
        working: Memory | None = None,
        episodic: Memory | None = None,
        semantic: Memory | None = None,
        policy: MemoryPolicy | None = None,
    ) -> None:

        self.working = (
            working
            if working is not None
            else WorkingMemory()
        )

        self.episodic = (
            episodic
            if episodic is not None
            else EpisodicMemory()
        )

        self.semantic = (
            semantic
            if semantic is not None
            else SemanticMemory()
        )

        self.policy = (
            policy
            if policy is not None
            else MemoryPolicy()
        )

    def _get_memory(
        self,
        kind: MemoryKind,
    ) -> Memory:

        mapping = {
            MemoryKind.WORKING: self.working,
            MemoryKind.EPISODIC: self.episodic,
            MemoryKind.SEMANTIC: self.semantic,
        }

        return mapping[kind]

    def store(
        self,
        item: MemoryItem,
        kind: MemoryKind,
    ) -> bool:

        memory = self._get_memory(kind)

        return memory.store(item)

    def update(
        self,
        kind: MemoryKind,
        item_id: str,
        content: str,
    ) -> MemoryItem:

        memory = self._get_memory(kind)

        return memory.update(item_id, content)

    def remember_message(
        self,
        message: Message,
        kind: MemoryKind = MemoryKind.SEMANTIC,
    ) -> bool:

        if not self.policy.should_store_memory(message):
            return False

        normalized = normalize_text(message.content)

        digest = hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()[:16]

        item = MemoryItem(
            id=f"message:{digest}",
            content=message.content,
            metadata={
                "role": message.role,
            },
        )

        return self.store(
            item=item,
            kind=kind,
        )

    def retrieve_relevant(
        self,
        query,
        limit: int = 5,
    ) -> list[MemoryItem]:

        try:
            candidates: list[MemoryItem] = []

            for memory in (
                self.working,
                self.semantic,
                self.episodic,
            ):
                candidates.extend(
                    memory.retrieve(    
                    query=query,
                    limit=limit,
                    )
                )
        except Exception as e:
            raise MemoryRetrievalError(
                f"Error retrieving memory: {e}"
            ) from e

        unique: dict[str, MemoryItem] = {}

        for item in candidates:
            key = normalize_text(item.content)
            unique[key] = item

        if not unique:
            for memory in (
                self.working,
                self.semantic,
                self.episodic,
            ):
                for item in memory.retrieve(
                    query="",
                    limit=limit,
                ):
                    key = normalize_text(item.content)
                    unique[key] = item

        ranked = list(unique.values())

        ranked.sort(
            key=lambda item: memory_score(
                item.content,
                query,
            ),
            reverse=True,
        )
        return ranked[:limit]

    
