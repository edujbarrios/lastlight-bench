from pathlib import Path

import pytest

from lastlight_bench.schema import load_cases


ROOT = Path(__file__).resolve().parents[1]


def test_dataset_has_expected_balance_and_unique_ids() -> None:
    cases = load_cases(ROOT / "datasets" / "eval.jsonl")
    assert len(cases) == 30
    assert len({case.id for case in cases}) == 30
    assert sum(case.answerable for case in cases) == 20
    assert sum(not case.answerable for case in cases) == 10
    assert {case.language for case in cases} == {"en", "es"}


def test_invalid_jsonl_reports_line(tmp_path: Path) -> None:
    dataset = tmp_path / "bad.jsonl"
    dataset.write_text('{"id": "ok"}\nnot-json\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad\.jsonl:1"):
        load_cases(dataset)

