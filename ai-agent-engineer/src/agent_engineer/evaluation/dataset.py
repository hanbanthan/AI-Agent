import json

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from agent_engineer.evaluation.case import (
    EvaluationCase,
    EvaluationCategory,
)

@dataclass
class EvaluationDataset:
    cases: list[EvaluationCase]

    def validate(self) -> None:

        ids: set[str] = set()

        for case in self.cases:
            case.validate()

            if case.id in ids:
                raise ValueError(
                    f"Duplicate EvaluationCase id found: {case.id}"
                )
            ids.add(case.id)

    def validate_distribution(self) -> None:
        counts = Counter(case.category for case in self.cases)

        expected = {
            EvaluationCategory.NORMAL: 20,
            EvaluationCategory.EDGE: 10,
            EvaluationCategory.ADVERSARIAL: 10,
            EvaluationCategory.TOOL_FAILURE: 10,
        }

        if counts != expected:
            raise ValueError(
                f"EvaluationDataset distribution mismatch. "
                f"Expected: {expected}, Found: {counts}"
            )

    @classmethod
    def from_jsonl(cls, path: Path) -> "EvaluationDataset":

        path = Path(path)

        cases: list[EvaluationCase] = []

        with path.open("r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)
                    case = EvaluationCase.from_dict(data)
                    cases.append(case)
                except Exception as e:
                    raise ValueError(
                        f"Error parsing EvaluationCase at line {line_number}: {e}"
                    ) from e

        dataset = cls(cases=cases)
        dataset.validate()
        return dataset

    def __len__(self) -> int:
        return len(self.cases)