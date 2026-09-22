from agent_engineer.memory.base import (
    InMemoryMemory,
    MemoryItem,
)

class WorkingMemory(InMemoryMemory):

    def __init__(
        self,
        capacity: int = 10,
    ) -> None:

        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")

        super().__init__()

        self.capacity = capacity

    def store(
        self,
        item: MemoryItem,
    ) -> bool:

        stored = super().store(item)

        if not stored:
            return False

        while len(self._items) > self.capacity:
            oldest_id = next(iter(self._items))
            del self._items[oldest_id]

        return True
