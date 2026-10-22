from __future__ import annotations

import argparse
from pathlib import Path

from .runner import run_benchmark, write_json


ROOT = Path(__file__).resolve().parents[2]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Benchmark LastLight retrieval and refusal behavior")
    value.add_argument("--corpus", type=Path, default=ROOT / "corpus" / "field-ops-v1")
    value.add_argument("--cases", type=Path, default=ROOT / "datasets" / "eval.jsonl")
    value.add_argument("--strategy", choices=("lexical", "bm25", "adaptive"), default="adaptive")
    value.add_argument("--mode", choices=("survival", "balanced", "accuracy"), default="balanced")
    value.add_argument("--top-k", type=int, default=3)
    value.add_argument("--warmup", type=int, default=3)
    value.add_argument("--energy-budget-mwh", type=float)
    value.add_argument("--memory-budget-mb", type=int)
    value.add_argument("--output", type=Path, default=ROOT / "results" / "latest.json")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = run_benchmark(
        args.corpus, args.cases, args.strategy, args.mode, args.top_k, args.warmup,
        args.energy_budget_mwh, args.memory_budget_mb,
    )
    write_json(result, args.output)
    summary = result["summary"]
    print(f"strategy={args.strategy} cases={summary['cases']} top1={summary['top1_accuracy']:.3f} "
          f"mrr={summary['mrr']:.3f} refusal_recall={summary['refusal_recall']:.3f} "
          f"p95_ms={summary['latency_ms_p95']:.3f}")
    return 0

