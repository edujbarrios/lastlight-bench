from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc
from typing import Any

from lastlight import LastLight

from .metrics import summarize
from .schema import Case, load_cases


def _rank(sources: tuple[Any, ...], expected_path: str | None) -> int | None:
    if expected_path is None:
        return None
    for position, source in enumerate(sources, 1):
        if source.path.replace("\\", "/") == expected_path:
            return position
    return None


def evaluate_case(engine: LastLight, case: Case, top_k: int) -> dict[str, object]:
    tracemalloc.start()
    started = time.perf_counter_ns()
    result = engine.query(case.query, top_k=top_k)
    latency_ms = (time.perf_counter_ns() - started) / 1_000_000
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rank = _rank(result.sources, case.expected_path)
    return {
        **asdict(case),
        "accepted": result.accepted,
        "confidence": result.confidence,
        "refusal_reason": result.refusal_reason,
        "top1_path": result.sources[0].path if result.sources else None,
        "top1_score": result.sources[0].score if result.sources else None,
        "expected_rank": rank,
        "top1_correct": rank == 1,
        "reciprocal_rank": 1.0 / rank if rank else 0.0,
        "latency_ms": latency_ms,
        "peak_memory_mib": peak_bytes / (1024 * 1024),
        "selected_strategy": result.retrieval.strategy,
        "effective_top_k": result.retrieval.effective_top_k,
        "risk": result.retrieval.risk,
        "decision_reason": result.decision.reason if result.decision else None,
    }


def run_benchmark(
    corpus: Path,
    cases_path: Path,
    strategy: str,
    mode: str,
    top_k: int,
    warmup: int,
    energy_budget_mwh: float | None = None,
    memory_budget_mb: int | None = None,
) -> dict[str, object]:
    cases = load_cases(cases_path)
    engine = LastLight(
        corpus,
        strategy=strategy,
        mode=mode,
        energy_budget_mwh=energy_budget_mwh,
        memory_budget_mb=memory_budget_mb,
    )
    for index in range(warmup):
        engine.query(cases[index % len(cases)].query, top_k=top_k)
    rows = [evaluate_case(engine, case, top_k) for case in cases]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "implementation": {"name": "lastlight", "version": _lastlight_version()},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
        },
        "configuration": {
            "strategy": strategy,
            "mode": mode,
            "top_k": top_k,
            "warmup": warmup,
            "energy_budget_mwh": energy_budget_mwh,
            "memory_budget_mb": memory_budget_mb,
            "corpus": str(corpus),
            "cases": str(cases_path),
        },
        "summary": summarize(rows),
        "cases": rows,
    }


def _lastlight_version() -> str:
    try:
        from importlib.metadata import version
        return version("lastlight")
    except Exception:  # pragma: no cover - editable source without package metadata
        return "unknown"


def write_json(result: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

