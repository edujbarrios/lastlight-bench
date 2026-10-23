# LastLight Bench

[![CI](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml)

A reproducible evaluation of [LastLight](https://github.com/edujbarrios/lastlight) as an offline retrieval system for resource-constrained environments. The benchmark measures document ranking, answer/refusal calibration, bilingual behavior, adaptive routing, latency, and Python allocation peaks through LastLight's public API.

> [!CAUTION]
> **The recommendations included in this corpus were produced by ChatGPT for benchmarking purposes.** In a real deployment, every statement must be independently verified and must follow the criteria, authority, and procedures of the responsible organization. Those internal criteria are normally private, so this repository uses synthetic documents that only emulate the structure of operational guidance. The dataset is exclusively for benchmark evaluation and must never be used for operational decisions.

## Benchmark design

The benchmark has four independently versioned layers:

1. **Corpus:** 32 long-form operational manuals, 15,606 words, 22 English documents and 10 Spanish documents.
2. **Ground truth:** 160 labeled queries—108 answerable and 52 expected refusals. Forty-eight queries are in Spanish.
3. **Execution matrix:** lexical, BM25, three adaptive modes, a 0.4 mWh policy budget, and a 64 MiB memory policy budget.
4. **Evaluation:** per-query results, aggregate metrics, and slices by language, difficulty, category, and tag.

The documents deliberately overlap. Water advisory, treatment, flushing, and pump-operation manuals share terminology; generator, electrical, battery, fuel, and refrigeration procedures intersect; radio, satellite, and formal-message protocols compete for similar queries. This prevents simple keyword matching from producing an artificially perfect result.

### What is evaluated

| Dimension | Concrete test |
|---|---|
| Retrieval quality | Whether the labeled document appears first and how highly it ranks overall. |
| Answer calibration | Whether LastLight answers supported questions and refuses unsupported ones. |
| Hard negatives | Questions that mention corpus terminology but request absent live state, identities, credentials, prescriptions, or authority decisions. |
| Near-neighbor discrimination | Whether LastLight separates manuals with shared entities, warnings, and procedures. |
| Bilingual retrieval | English and Spanish queries against a single mixed-language pack. |
| Query difficulty | Direct lookup, paraphrase, numeric constraints, negation, multi-condition, contrastive, and multi-step cases. |
| Adaptive policy | Strategy and `top_k` selected under survival, balanced, accuracy, energy, and memory policies. |
| Efficiency | Warmed query latency and peak Python allocations on the measured host. |
| Auditability | Source path, score, confidence, matched terms, refusal reason, and planner decision retained per case. |

This is a closed-corpus retrieval benchmark. It does not score generated prose, verify the real-world truth of synthetic recommendations, measure physical energy consumption, or claim generalization to unrelated corpora.

## Baseline results

LastLight 0.2.2, Python 3.12, Windows 11, `top_k=3`, three warm-up queries:

| Strategy / mode | Top-1 | MRR | Answer precision | Answerable recall | Refusal recall | False accept | Mean ms | P95 ms | Peak MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical / balanced | 77.8% | 0.867 | 80.5% | 64.8% | 88.5% | 11.5% | 217.82 | 335.96 | 0.73 |
| bm25 / balanced | 86.1% | 0.921 | 92.9% | 48.1% | 100.0% | 0.0% | 195.65 | 253.27 | 0.73 |
| adaptive / survival | 77.8% | 0.861 | 80.5% | 64.8% | 88.5% | 11.5% | 177.94 | 236.27 | 0.73 |
| adaptive / balanced | 83.3% | 0.910 | 90.2% | 50.9% | 98.1% | 1.9% | 207.83 | 273.55 | 0.73 |
| adaptive / accuracy | 86.1% | 0.921 | 92.7% | 47.2% | 100.0% | 0.0% | 220.94 | 277.22 | 0.73 |
| adaptive / balanced / 0.4 mWh | 77.8% | 0.861 | 80.5% | 64.8% | 88.5% | 11.5% | 204.16 | 257.61 | 0.73 |
| adaptive / balanced / 64 MiB | 77.8% | 0.861 | 80.5% | 64.8% | 88.5% | 11.5% | 212.07 | 265.49 | 0.73 |

LastLight 0.2.2 fixes the major calibration failure observed in 0.2.1. BM25 now refuses all 52 unsupported queries, reducing false acceptance from 96.2% to 0%, while answer precision rises from 58.9% to 92.9%. The trade-off is deliberate but substantial: BM25 answerable recall falls from 86.1% to 48.1%. Lexical is less conservative, retaining 64.8% answerable recall with an 11.5% false-accept rate. The new policy strongly improves safety, but future calibration work should recover supported answers without reopening hard negatives.

### Bilingual retrieval

| Configuration | English Top-1 | Spanish Top-1 | English answerable recall | Spanish answerable recall |
|---|---:|---:|---:|---:|
| lexical | 80.3% | 71.9% | 64.5% | 65.6% |
| BM25 | 86.8% | 84.4% | 47.4% | 50.0% |
| adaptive balanced | 84.2% | 81.2% | 48.7% | 56.2% |

Spanish ranking remains close to English ranking. Spanish answerable recall is slightly higher under the calibrated policies, while Spanish refusal recall ranges from 93.8% to 100%. The comparison is meaningful because Spanish is represented by full-length competing manuals and hard negatives, rather than a few demonstration queries.

Host-sensitive latency and allocation values are descriptive, not universal product claims. The complete per-case artifact is committed at [`results/baseline.json`](results/baseline.json).

## Metric definitions

| Metric | Definition |
|---|---|
| Top-1 | Answerable cases whose labeled document is ranked first / answerable cases. |
| MRR | Mean reciprocal rank of the labeled document across answerable cases. |
| Answer precision | Correctly accepted answerable cases / all accepted cases. |
| Answerable recall | Correctly accepted answerable cases / answerable cases. |
| Refusal recall | Refused unanswerable cases / unanswerable cases. |
| False accept | Accepted unanswerable cases / unanswerable cases. |
| Mean / P95 ms | Wall-clock `LastLight.query` latency after warm-up. |
| Peak MiB | Peak Python allocation measured with `tracemalloc`, not process RSS. |

Lexical and BM25 score scales are strategy-specific and are never compared directly. No composite score hides the ranking/calibration trade-off.

## Reproduce

```bash
git clone https://github.com/edujbarrios/lastlight-bench.git
cd lastlight-bench
python -m venv .venv
python -m pip install -e ".[dev]"
lastlight-bench-suite --output results/local.json
lastlight-bench-gate results/local.json
```

Focused runs:

```bash
lastlight-bench --strategy lexical --output results/lexical.json
lastlight-bench --strategy adaptive --mode survival --output results/survival.json
lastlight-bench --strategy adaptive --energy-budget-mwh 0.4 --output results/low-energy.json
```

The energy and memory values exercise LastLight's planning policy; they are not measurements of physical energy or process RSS.

## Repository structure

```text
corpus/field-ops-v1/   versioned bilingual LastLight pack
datasets/eval.jsonl    query-level labels and experimental slices
src/lastlight_bench/   runner, metrics, reports, suite, and gates
results/baseline.json  raw reproducible baseline artifact
tests/                 corpus, schema, metric, integration, and gate tests
.github/workflows/     Python matrix and deterministic benchmark CI
```

Every JSONL case declares `id`, `query`, `language`, `category`, `answerable`, `expected_path`, `difficulty`, and `tags`. Corpus changes and label changes therefore produce explicit reviewable diffs.

## CI and regression policy

Pull requests run unit and integration tests on Python 3.10–3.12 and execute the seven-condition matrix on Python 3.12. For LastLight 0.2.2 and corpus v3.0, regression floors are Top-1 ≥ 0.77, MRR ≥ 0.86, answer precision ≥ 0.78, answerable recall ≥ 0.45, and refusal recall ≥ 0.85. These floors protect the new refusal behavior while allowing the documented strategy trade-off. They are failure-detection floors, not quality targets. Latency is not gated on shared CI hardware.

## License

Mozilla Public License 2.0. The synthetic corpus is marked CC0-1.0 in its pack manifest.
