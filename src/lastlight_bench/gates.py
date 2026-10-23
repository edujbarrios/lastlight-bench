from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_GATES = {
    "top1_accuracy": 0.77,
    "mrr": 0.86,
    "answer_precision": 0.57,
    "answerable_recall": 0.75,
    "refusal_recall": 0.03,
}


def check_artifact(path: Path, gates: dict[str, float] | None = None) -> list[str]:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    thresholds = gates or DEFAULT_GATES
    for run in artifact.get("runs", []):
        config = run["configuration"]
        label = f"{config['strategy']}/{config['mode']}"
        for metric, minimum in thresholds.items():
            actual = float(run["summary"][metric])
            if actual < minimum:
                failures.append(f"{label}: {metric}={actual:.4f} below {minimum:.4f}")
    if not artifact.get("runs"):
        failures.append("artifact contains no runs")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply quality gates to a benchmark artifact")
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    failures = check_artifact(args.artifact)
    if failures:
        print("Benchmark gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Benchmark quality gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
