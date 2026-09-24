import pytest

from agent_engineer.evaluation.judge import (
    JudgeResult,
    MockJudge,
    LLMJudge,
    JudgeRubric,
    parse_judge_response,
    InvalidJudgeResponseError,
)

from agent_engineer.llm.mock import MockLLM
from agent_engineer.llm.types import (
    LLMResponse,
)
def test_judge_output_parsing() -> None:
    rubric = JudgeRubric.default()

    content = """
    {
        "scores": {
            "correctness": 5,
            "completeness": 4,
            "tool_use": 5,
            "groundedness": 4,
            "safety": 5
        },
        "reasons": {
            "correctness": "Correct answer.",
            "completeness": "Mostly complete.",
            "tool_use": "Tool was appropriate.",
            "groundedness": "Supported by context.",
            "safety": "No safety issue."
        }
    }
    """

    result = parse_judge_response(
        content=content,
        rubric=rubric,
    )

    assert result.scores["correctness"] == 5
    assert result.scores["completeness"] == 4

    assert 1.0 <= result.overall_score <= 5.0

def test_invalid_judge_response() -> None:
    rubric = JudgeRubric.default()

    with pytest.raises(
        InvalidJudgeResponseError
    ):
        parse_judge_response(
            content="this is not json",
            rubric=rubric,
        )

def test_score_must_be_in_bounds() -> None:
    rubric = JudgeRubric.default()

    content = """
    {
        "scores": {
            "correctness": 9,
            "completeness": 4,
            "tool_use": 4,
            "groundedness": 4,
            "safety": 4
        },
        "reasons": {
            "correctness": "Reason",
            "completeness": "Reason",
            "tool_use": "Reason",
            "groundedness": "Reason",
            "safety": "Reason"
        }
    }
    """

    with pytest.raises(
        InvalidJudgeResponseError,
        match="between 1 and 5",
    ):
        parse_judge_response(
            content=content,
            rubric=rubric,
        )

def test_missing_criterion_is_invalid() -> None:
    rubric = JudgeRubric.default()

    content = """
    {
        "scores": {
            "correctness": 5,
            "completeness": 5,
            "tool_use": 5,
            "groundedness": 5
        },
        "reasons": {
            "correctness": "Good",
            "completeness": "Good",
            "tool_use": "Good",
            "groundedness": "Good",
            "safety": "Good"
        }
    }
    """

    with pytest.raises(
        InvalidJudgeResponseError,
        match="safety",
    ):
        parse_judge_response(
            content=content,
            rubric=rubric,
        )

def test_mock_judge_is_deterministic() -> None:

    expected = JudgeResult(
        scores={
            "correctness": 5.0,
            "completeness": 4.0,
            "tool_use": 5.0,
            "groundedness": 4.0,
            "safety": 5.0,
        },
        reasons={
            "correctness": "Correct.",
            "completeness": "Complete enough.",
            "tool_use": "Good.",
            "groundedness": "Grounded.",
            "safety": "Safe.",
        },
        overall_score=4.6,
    )

    judge = MockJudge(expected)

    first = judge.evaluate(
        question="What is 2 + 2?",
        answer="4",
    )

    second = judge.evaluate(
        question="What is 2 + 2?",
        answer="4",
    )

    assert first == expected
    assert second == expected
    assert first == second

    assert len(judge.calls) == 2

def test_llm_judge_uses_llm() -> None:

    llm = MockLLM(
        responses=[
            LLMResponse(
                content="""
                {
                    "scores": {
                        "correctness": 5,
                        "completeness": 5,
                        "tool_use": 4,
                        "groundedness": 5,
                        "safety": 5
                    },
                    "reasons": {
                        "correctness": "Correct.",
                        "completeness": "Complete.",
                        "tool_use": "Appropriate.",
                        "groundedness": "Grounded.",
                        "safety": "Safe."
                    }
                }
                """,
                model="mock-model",
            )
        ]
    )

    judge = LLMJudge(llm=llm)

    result = judge.evaluate(
        question="What is 2 + 2?",
        answer="4",
        reference_answer="4",
    )

    assert result.scores["correctness"] == 5
    assert len(llm.requests) == 1