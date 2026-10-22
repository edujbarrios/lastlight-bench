from pathlib import Path

from lastlight_bench.runner import run_benchmark


ROOT = Path(__file__).resolve().parents[1]


def test_lexical_smoke_run_uses_public_api() -> None:
    result = run_benchmark(
        ROOT / "corpus" / "field-ops-v1",
        ROOT / "datasets" / "eval.jsonl",
        strategy="lexical",
        mode="balanced",
        top_k=3,
        warmup=1,
    )
    assert result["implementation"]["name"] == "lastlight"
    assert result["summary"]["cases"] == 60
    assert result["summary"]["top1_accuracy"] >= 0.85
    assert result["summary"]["refusal_recall"] >= 0.50

