from agent_engineer.memory import (
    MemoryItem,
    SemanticMemory,
)

def test_store_memory() -> None:
    memory = SemanticMemory()

    item = MemoryItem(
        id="1",
        content="User prefers Python",
    )

    assert memory.store(item) is True
    assert len(memory._items) == 1


def test_retrieve_memory() -> None:
    memory = SemanticMemory()

    memory.store(
        MemoryItem(
            id="1",
            content="User prefers Python",
        )
    )

    memory.store(
        MemoryItem(
            id="2",
            content="User studies databases",
        )
    )

    results = memory.retrieve(
        "Python",
        limit=5,
    )

    assert len(results) == 1
    assert results[0].id == "1"



def test_update_memory() -> None:
    memory = SemanticMemory()

    memory.store(
        MemoryItem(
            id="1",
            content="User prefers Java",
        )
    )

    updated = memory.update(
        item_id="1",
        content="User prefers Python",
    )

    assert (
        updated.content
        == "User prefers Python"
    )

def test_duplicate_memory_not_stored() -> None:
    memory = SemanticMemory()

    first = MemoryItem(
        id="1",
        content="User prefers Python",
    )

    duplicate = MemoryItem(
        id="2",
        content="User prefers Python",
    )

    assert memory.store(first) is True
    assert memory.store(duplicate) is False

    assert len(memory) == 1