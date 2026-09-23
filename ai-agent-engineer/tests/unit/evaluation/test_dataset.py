import pytest
from pathlib import Path

from agent_engineer.evaluation import (
    EvaluationCase,
    EvaluationCategory,
    EvaluationDataset,
)


def test_duplicate_case_id_is_invalid() -> None:

    dataset = EvaluationDataset(
        cases=[
            EvaluationCase(
                id="case-1",
                category=EvaluationCategory.NORMAL,
                input="Hello",
            ),
            EvaluationCase(
                id="case-1",
                category=EvaluationCategory.EDGE,
                input="Test",
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        dataset.validate()

def test_real_dataset_has_correct_distribution() -> None:

    dataset = EvaluationDataset.from_jsonl(
        Path(__file__).resolve().parents[3]
        / "data"
        / "evaluation"
        / "agent_cases.jsonl"
    )

    assert len(dataset) == 50

    dataset.validate_distribution()