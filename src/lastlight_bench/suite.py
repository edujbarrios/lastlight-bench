from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .reporting import corpus_stats, markdown_table, slice_metrics
from .runner import run_benchmark


ROOT = Path(__file__).resolve().parents[2]
CONFIGURATIONS = (
    {"strategy": "lexical", "mode": "balanced"},
    {"strategy": "bm25", "mode": "balanced"},
    {"strategy": "adaptive", "mode": "survival"},
    {"strategy": "adaptive", "mode": "balanced"},
    {"strategy": "adaptive", "mode": "accuracy"},
    {"strategy": "adaptive", "mode": "balanced", "energy_budget_mwh": 0.4},
    {"strategy": "adaptive", "mode": "balanced", "memory_budget_mb": 64},
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the complete LastLight benchmark matrix")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "baseline.json")
    parser.add_argument("--warmup", type=int, default=3)
    args = parser.parse_args(argv)
    corpus = ROOT / "corpus" / "field-ops-v1"
    cases = ROOT / "datasets" / "eval.jsonl"
    results = []
    for configuration in CONFIGURATIONS:
        result = run_benchmark(corpus, cases, top_k=3, warmup=args.warmup, **configuration)
        result["breakdown"] = {
            key: slice_metrics(result["cases"], key)
            for key in ("difficulty", "language", "category", "tags")
        }
        results.append(result)
        print(f"finished {configuration}")
    artifact = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {"synthetic": True, **corpus_stats(corpus), "cases": len(results[0]["cases"])},
        "runs": results,
        "markdown": markdown_table(results),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n" + artifact["markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

