from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


@dataclass(slots=True)
class ValidationIssue:
    category: str
    message: str
    slide_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "category": self.category,
            "message": self.message,
            "slide_id": self.slide_id,
        }


@dataclass(slots=True)
class ValidationReport:
    status: str
    issues: list[ValidationIssue]

    @classmethod
    def from_issues(cls, issues: Iterable[ValidationIssue]) -> "ValidationReport":
        normalized = list(issues)
        status = "failed" if normalized else "passed"
        return cls(status=status, issues=normalized)

    def to_dict(self) -> dict[str, Sequence[Mapping[str, str | None]]]:
        return {
            "status": self.status,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def write_validation_report(root: Path, report: ValidationReport) -> None:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "validation.json"
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
