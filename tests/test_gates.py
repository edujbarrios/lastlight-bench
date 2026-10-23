import json
from pathlib import Path

from lastlight_bench.gates import check_artifact


def test_gate_reports_metric_and_configuration(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps({"runs": [{
        "configuration": {"strategy": "bm25", "mode": "balanced"},
        "summary": {"top1_accuracy": 0.5},
    }]}), encoding="utf-8")
    failures = check_artifact(artifact, {"top1_accuracy": 0.9})
    assert failures == ["bm25/balanced: top1_accuracy=0.5000 below 0.9000"]

