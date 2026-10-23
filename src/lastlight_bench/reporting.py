from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable


def slice_metrics(rows: list[dict[str, object]], key: str) -> dict[str, dict[str, float | int]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        value = row[key]
        values: Iterable[object] = value if isinstance(value, (tuple, list)) else (value,)
        for item in values:
            groups[str(item)].append(row)
    return {name: _quality(group) for name, group in sorted(groups.items())}


def _quality(rows: list[dict[str, object]]) -> dict[str, float | int]:
    answerable = [row for row in rows if bool(row["answerable"])]
    unanswerable = [row for row in rows if not bool(row["answerable"])]
    accepted = [row for row in rows if bool(row["accepted"])]
    correct = [row for row in answerable if bool(row["accepted"]) and bool(row["top1_correct"])]
    return {
        "cases": len(rows),
        "top1_accuracy": _div(sum(bool(row["top1_correct"]) for row in answerable), len(answerable)),
        "answer_precision": _div(len(correct), len(accepted)),
        "answerable_recall": _div(len(correct), len(answerable)),
        "refusal_recall": _div(sum(not bool(row["accepted"]) for row in unanswerable), len(unanswerable)),
    }


def _div(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def corpus_stats(corpus: Path) -> dict[str, int]:
    documents = list(corpus.rglob("*.md"))
    words = sum(len(path.read_text(encoding="utf-8").split()) for path in documents)
    return {"documents": len(documents), "words": words, "languages": len({p.parts[-3] for p in documents})}


def markdown_table(results: list[dict[str, object]]) -> str:
    lines = [
        "| Strategy / mode | Top-1 | MRR | Answer precision | Answerable recall | Refusal recall | False accept | Mean ms | P95 ms | Peak MiB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        config, summary = result["configuration"], result["summary"]
        label = f"{config['strategy']} / {config['mode']}"
        if config.get("energy_budget_mwh"):
            label += f" / {config['energy_budget_mwh']} mWh"
        if config.get("memory_budget_mb"):
            label += f" / {config['memory_budget_mb']} MiB"
        lines.append(
            f"| {label} | {summary['top1_accuracy']:.1%} | {summary['mrr']:.3f} | "
            f"{summary['answer_precision']:.1%} | {summary['answerable_recall']:.1%} | "
            f"{summary['refusal_recall']:.1%} | {summary['false_accept_rate']:.1%} | "
            f"{summary['latency_ms_mean']:.2f} | {summary['latency_ms_p95']:.2f} | "
            f"{summary['peak_memory_mib']:.2f} |"
        )
    return "\n".join(lines)

