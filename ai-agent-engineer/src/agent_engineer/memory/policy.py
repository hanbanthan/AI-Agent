from collections.abc import Callable

from agent_engineer.llm.types import Message

class MemoryPolicy:

    def __init__(
        self,
        predicate: (
            Callable[[Message], bool]
            | None
        ) = None,
    ) -> None:

        self._predicate = (
            predicate
            or self._default_policy
        )

    def should_store_memory(
        self,
        message: Message,
    ) -> bool:

        return self._predicate(message)

    def _default_policy(self, message: Message) -> bool:

        if message.role != "user":
            return False

        content = message.content.strip().lower()

        if not content:
            return False

        memory_signals = (
            "remember ",
            "i prefer ",
            "i like ",
            "i use ",
            "my name is ",
            "hãy nhớ ",
            "tôi thích ",
            "mình thích ",
            "tôi dùng ",
            "mình dùng ",
        )

        return any(
            signal in content
            for signal in memory_signals
        )