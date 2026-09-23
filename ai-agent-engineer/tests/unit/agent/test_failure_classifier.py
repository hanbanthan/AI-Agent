from agent_engineer.failure import (
    FailureCategory,
    FailureClassifier,
)
from agent_engineer.llm.errors import (
    LLMTimeoutError,
)
from agent_engineer.tools.errors import (
    ToolNotFoundError,
)


def test_classify_llm_failure() -> None:

    classifier = FailureClassifier()

    result = classifier.classify(
        LLMTimeoutError("timeout")
    )

    assert (
        result.category
        == FailureCategory.LLM
    )

    assert result.retryable is True


def test_classify_tool_failure() -> None:

    classifier = FailureClassifier()

    result = classifier.classify(
        ToolNotFoundError(
            "calculator"
        )
    )

    assert (
        result.category
        == FailureCategory.TOOL
    )

    assert result.retryable is False