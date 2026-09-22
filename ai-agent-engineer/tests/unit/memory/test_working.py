from agent_engineer.memory import (
    MemoryItem,
    WorkingMemory,
)


def test_working_memory_eviction() -> None:

    memory = WorkingMemory(
        capacity=2
    )

    memory.store(
        MemoryItem(
            id="1",
            content="First memory",
        )
    )

    memory.store(
        MemoryItem(
            id="2",
            content="Second memory",
        )
    )

    memory.store(
        MemoryItem(
            id="3",
            content="Third memory",
        )
    )

    assert len(memory) == 2

    assert memory.retrieve(
        "",
        limit=10,
    ) == [
        MemoryItem(
            id="2",
            content="Second memory",
        ),
        MemoryItem(
            id="3",
            content="Third memory",
        ),
    ]