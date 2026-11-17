# LastLight Bench

[![CI](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml)

A reproducible benchmark for [LastLight](https://github.com/edujbarrios/lastlight) using official Spanish and Italian medicine documents extracted from CIMA/AEMPS and AIFA. It measures document ranking, answer/refusal calibration, bilingual behavior, and query latency through LastLight's public API.

> [!CAUTION]
> The corpus contains official medicine information, but this repository is a retrieval benchmark and must not be used for diagnosis, prescribing, dosing, or other medical decisions. Always consult the current official source and an appropriate healthcare professional.

## Benchmark design

The benchmark has four independently versioned layers:

1. **Corpus:** 200 official medicine documents (10 per therapeutic category and language), 1,171,017 words, in Spanish and Italian.
2. **Ground truth:** 60 labeled queries: 40 answerable active-ingredient lookups and 20 hard negatives requiring live pharmacy stock or personalized dosing.
3. **Execution matrix:** lexical, BM25, and hybrid retrieval in balanced mode.
4. **Evaluation:** per-query results, aggregate metrics, and slices by language, difficulty, category, and tag.

The corpus is pinned from `medicine-pack-extractor@2d10e489dbe602ecf7cae36dd0fd3a668155f542`. The selected slice and extractor configuration are committed in [`datasets/medicine-pack-slice.json`](datasets/medicine-pack-slice.json) and [`datasets/medicine-pack-config.json`](datasets/medicine-pack-config.json). The deterministic case generator is [`scripts/generate_medicine_dataset.py`](scripts/generate_medicine_dataset.py).

This is a closed-corpus retrieval benchmark. It does not assess the clinical truth or completeness of an answer, generated prose, or generalization to unrelated corpora.

## Metrics

| Metric | Definition |
|---|---|
| Top-1 | Answerable cases whose labeled document is ranked first / answerable cases. |
| MRR | Mean reciprocal rank of the labeled document across answerable cases. |
| Answer precision | Correctly accepted answerable cases / all accepted cases. |
| Answerable recall | Correctly accepted answerable cases / answerable cases. |
| Refusal recall | Refused unanswerable cases / unanswerable cases. |
| False accept | Accepted unanswerable cases / unanswerable cases. |
| Mean / P95 ms | Wall-clock `LastLight.query` latency after warm-up. |

Memory measurement is disabled because `tracemalloc` materially distorts full-pack query latency. Latency is host-sensitive and is descriptive, not a universal product claim.

## Baseline results

LastLight 0.3.1, `top_k=3`, three warm-up queries:

| Strategy / mode | Top-1 | MRR | Answer precision | Answerable recall | Refusal recall | False accept | Mean ms | P95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical / balanced | 95.0% | 0.975 | 100.0% | 50.0% | 100.0% | 0.0% | 8,938.48 | 11,621.36 |
| bm25 / balanced | 97.5% | 0.975 | 95.5% | 52.5% | 100.0% | 0.0% | 5,065.24 | 11,276.39 |
| hybrid / balanced | 97.5% | 0.975 | 100.0% | 52.5% | 100.0% | 0.0% | 7,514.31 | 11,730.93 |

All strategies refused every hard negative. BM25 and hybrid reached the best Top-1 and answerable recall; lexical and hybrid had no incorrect accepted answers. The full official pack also exposes a substantial latency increase compared with the previous small synthetic corpus.

### Language slices

| Strategy | Spanish Top-1 | Italian Top-1 | Spanish answerable recall | Italian answerable recall |
|---|---:|---:|---:|---:|
| lexical | 90.0% | 100.0% | 90.0% | 10.0% |
| BM25 | 95.0% | 100.0% | 65.0% | 40.0% |
| hybrid | 95.0% | 100.0% | 75.0% | 30.0% |

Ranking is strong in both languages, while acceptance is much more conservative for Italian. This gap is visible rather than hidden by the aggregate score. The complete per-case artifact is committed at [`results/baseline.json`](results/baseline.json).

## Reproduce

```bash
git clone https://github.com/edujbarrios/lastlight-bench.git
cd lastlight-bench
python -m venv .venv
python -m pip install -e ".[dev]"
python scripts/generate_medicine_dataset.py
lastlight-bench-suite --output results/local.json
lastlight-bench-gate results/local.json
```

Focused runs:

```bash
lastlight-bench --strategy lexical --output results/lexical.json
lastlight-bench --strategy bm25 --output results/bm25.json
lastlight-bench --strategy hybrid --output results/hybrid.json
```

## Repository structure

```text
corpus/official-medicines-es-it/  pinned bilingual LastLight pack
datasets/                         labels and extractor slice/configuration
scripts/                          deterministic dataset generation
src/lastlight_bench/              runner, metrics, reporting, suite, and gates
results/baseline.json             raw reproducible baseline artifact
tests/                            corpus, schema, metric, integration, and gate tests
```

Every JSONL case declares `id`, `query`, `language`, `category`, `answerable`, `expected_path`, `difficulty`, and `tags`. Corpus and label changes therefore produce explicit reviewable diffs.

## License

Mozilla Public License 2.0. Refer to the pack manifest and original CIMA/AEMPS and AIFA sources for source-data provenance and terms.
