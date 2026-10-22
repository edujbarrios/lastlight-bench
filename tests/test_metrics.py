import pytest

from lastlight_bench.metrics import percentile, summarize


def row(*, answerable: bool, accepted: bool, correct: bool, rank: float, latency: float) -> dict[str, object]:
    return {
        "answerable": answerable,
        "accepted": accepted,
        "top1_correct": correct,
        "reciprocal_rank": rank,
        "latency_ms": latency,
        "peak_memory_mib": 1.0,
    }


def test_summary_keeps_retrieval_and_decision_metrics_separate() -> None:
    summary = summarize([
        row(answerable=True, accepted=True, correct=True, rank=1.0, latency=1.0),
        row(answerable=True, accepted=False, correct=True, rank=1.0, latency=2.0),
        row(answerable=False, accepted=True, correct=False, rank=0.0, latency=3.0),
        row(answerable=False, accepted=False, correct=False, rank=0.0, latency=4.0),
    ])
    assert summary["top1_accuracy"] == 1.0
    assert summary["answer_precision"] == 0.5
    assert summary["answerable_recall"] == 0.5
    assert summary["refusal_recall"] == 0.5
    assert summary["false_accept_rate"] == 0.5


def test_percentile_is_linearly_interpolated() -> None:
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == pytest.approx(2.5)

