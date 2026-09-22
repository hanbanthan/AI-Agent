from agent_engineer.agent import Agent
from agent_engineer.llm import (
    LLMResponse,
    MockLLM,
)

from agent_engineer.memory.manager import (
    MemoryItem,
    MemoryKind,
    MemoryManager,
)

def test_agent_receives_relevant_memory() -> None:

    manager = MemoryManager()

    manager.store(
        item=MemoryItem(
            id="1",
            content="User prefers Python",
        ),
        kind=MemoryKind.SEMANTIC,
    )

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="You prefer Python.",
                model="mock-model",
            )
        ]
    )

    agent = Agent(
        llm=llm,
        memory_manager=manager,
    )

    result = agent.run(
        "What programming language do I prefer?"
    )

    assert result.answer == ("You prefer Python.")

    request = llm.requests[0]

    memory_messages = [
        message
        for message in request.messages
        if (
            message.role == "system"
            and "Relevant memories" in message.content
        )
    ]

    assert len(memory_messages) == 1

    assert len(memory_messages) == 1

    assert "User prefers Python" in memory_messages[0].content

def test_agent_does_not_store_every_message() -> None:

    manager = MemoryManager()

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="Python is a language.",
                model="mock-model",
            )
        ]
    )

    agent = Agent(
        llm=llm,
        memory_manager=manager,
    )

    agent.run("What is Python?")

    assert len(manager.semantic) == 0