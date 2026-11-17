from pathlib import Path

from lastlight_bench.runner import run_benchmark


ROOT = Path(__file__).resolve().parents[1]


def test_lexical_smoke_run_uses_public_api(tmp_path: Path) -> None:
    cases = tmp_path / "smoke.jsonl"
    cases.write_text(
        (ROOT / "datasets" / "eval.jsonl").read_text(encoding="utf-8").splitlines()[0] + "\n",
        encoding="utf-8",
    )
    result = run_benchmark(
        ROOT / "corpus" / "official-medicines-es-it",
        cases,
        strategy="lexical",
        mode="balanced",
        top_k=3,
        warmup=1,
    )
    assert result["implementation"]["name"] == "lastlight"
    assert result["summary"]["cases"] == 1
    assert result["summary"]["top1_accuracy"] >= 0.70
    assert "refusal_code" in result["cases"][0]
    assert "top1_calibrated_score" in result["cases"][0]
    assert "top1_passage" in result["cases"][0]

