from agent_engineer.agent.state import AgentState
from agent_engineer.llm import Message

def test_agent_state_initial_values() -> None:
    state = AgentState()

    assert state.messages == []
    assert state.step_count == 0
    assert state.finished is False


def test_agent_state_add_message() -> None:
    state = AgentState()

    message = Message(
        role="user",
        content="Hello",
    )

    state.add_message(message)

    assert state.messages == [message]


def test_agent_state_increment_step() -> None:
    state = AgentState()

    state.increment_step()
    state.increment_step()

    assert state.step_count == 2


def test_agent_state_mark_finished() -> None:
    state = AgentState()

    state.mark_finished()

    assert state.finished is True
