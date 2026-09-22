from agent_engineer.llm.types import Message

import pytest

from agent_engineer.memory.base import (
    Memory,
    MemoryItem,
)
from agent_engineer.memory.errors import (
    MemoryRetrievalError,
)
from agent_engineer.memory.manager import (
    MemoryManager,
)



def test_irrelevant_message_is_not_stored() -> None:

    manager = MemoryManager()

    stored = manager.remember_message(
        Message(
            role="user",
            content="What is Python?",
        )
    )

    assert stored is False

    assert len(manager.semantic) == 0

def test_relevant_message_is_stored() -> None:

    manager = MemoryManager()

    stored = manager.remember_message(
        Message(
            role="user",
            content="I prefer Python.",
        )
    )

    assert stored is True
    assert len(manager.semantic) == 1

class BrokenMemory(Memory):

    def store(
        self,
        item: MemoryItem,
    ) -> bool:
        return True

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[MemoryItem]:

        raise RuntimeError(
            "Memory backend unavailable"
        )

    def update(
        self,
        item_id: str,
        content: str,
    ) -> MemoryItem:

        raise RuntimeError()


def test_memory_retrieval_failure() -> None:

    manager = MemoryManager(
        semantic=BrokenMemory()
    )

    with pytest.raises(
        MemoryRetrievalError,
        match="Memory backend unavailable",
    ):
        manager.retrieve_relevant(
            "Python"
        )