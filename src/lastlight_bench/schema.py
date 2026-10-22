from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class Case:
    id: str
    query: str
    language: str
    category: str
    answerable: bool
    expected_path: str | None
    difficulty: str
    tags: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "Case":
        return cls(
            id=str(value["id"]),
            query=str(value["query"]),
            language=str(value["language"]),
            category=str(value["category"]),
            answerable=bool(value["answerable"]),
            expected_path=str(value["expected_path"]) if value.get("expected_path") else None,
            difficulty=str(value["difficulty"]),
            tags=tuple(str(tag) for tag in value.get("tags", [])),
        )


def load_cases(path: Path) -> list[Case]:
    cases: list[Case] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            cases.append(Case.from_dict(json.loads(line)))
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid case at {path}:{line_number}: {error}") from error
    if not cases:
        raise ValueError(f"no benchmark cases found in {path}")
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("benchmark case ids must be unique")
    return cases

