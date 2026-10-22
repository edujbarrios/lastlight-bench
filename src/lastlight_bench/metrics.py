from __future__ import annotations

import math
import statistics
from typing import Iterable


def percentile(values: Iterable[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def safe_div(numerator: int | float, denominator: int | float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    answerable = [row for row in rows if row["answerable"]]
    unanswerable = [row for row in rows if not row["answerable"]]
    retrieved = [row for row in answerable if row["top1_correct"]]
    accepted = [row for row in rows if row["accepted"]]
    correct_accepts = [row for row in answerable if row["accepted"] and row["top1_correct"]]
    latencies = [float(row["latency_ms"]) for row in rows]
    reciprocal_ranks = [float(row["reciprocal_rank"]) for row in answerable]
    return {
        "cases": len(rows),
        "answerable_cases": len(answerable),
        "unanswerable_cases": len(unanswerable),
        "top1_accuracy": safe_div(len(retrieved), len(answerable)),
        "mrr": statistics.fmean(reciprocal_ranks) if reciprocal_ranks else 0.0,
        "answer_precision": safe_div(len(correct_accepts), len(accepted)),
        "answerable_recall": safe_div(len(correct_accepts), len(answerable)),
        "refusal_recall": safe_div(sum(not bool(row["accepted"]) for row in unanswerable), len(unanswerable)),
        "false_accept_rate": safe_div(sum(bool(row["accepted"]) for row in unanswerable), len(unanswerable)),
        "latency_ms_mean": statistics.fmean(latencies) if latencies else 0.0,
        "latency_ms_p50": percentile(latencies, 0.50),
        "latency_ms_p95": percentile(latencies, 0.95),
        "peak_memory_mib": max((float(row["peak_memory_mib"]) for row in rows), default=0.0),
    }

