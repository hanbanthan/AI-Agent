import pytest

from agent_engineer.llm.types import Message
from agent_engineer.memory.policy import MemoryPolicy


@pytest.mark.parametrize(
    ("role", "content", "expected"),
    [
        ("user", "I prefer Python.", True),
        ("user", "I like machine learning.", True),
        ("user", "I use Linux.", True),
        ("user", "My name is Giap.", True),
        ("user", "Remember that I use pytest.", True),
        ("user", "Tôi thích Python.", True),
        ("user", "Mình dùng Linux.", True),

        ("user", "Hello", False),
        ("user", "What is Python?", False),
        ("user", "", False),
        ("assistant", "I prefer Python.", False),
        ("tool", "Remember this value.", False),
    ],
)

def test_memory_policy(
    role,
    content,
    expected,
) -> None:

    policy = MemoryPolicy()

    message = Message(
        role=role,
        content=content,
    )

    assert policy.should_store_memory(message) is expected