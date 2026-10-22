# LastLight Bench

[![CI](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml)

An auditable benchmark of [LastLight](https://github.com/edujbarrios/lastlight), the dependency-free offline retrieval library for degraded-infrastructure scenarios. It measures retrieval, answer/refusal calibration, latency, Python allocation peaks, multilingual routing, and adaptive policy selection through LastLight's public API.

> [!CAUTION]
> **The corpus and every evaluation question were invented by ChatGPT.** They simulate the content, structure, ambiguity, and operational language of a realistic municipal emergency-operations document set. They do not describe a real organization, are not expert-validated, and must never be used as medical, public-health, electrical, food-safety, or emergency guidance.

## Baseline results

Measured on LastLight 0.2.1 / Python 3.12 / Windows 11, with 30 cases, `top_k=3`, and three warm-up queries. Latency and allocation numbers are single-host observations, not universal product claims. Accuracy is deterministic for the pinned corpus and package version.

| Strategy / mode | Top-1 | MRR | Answer precision | Answerable recall | Refusal recall | False accept | Mean ms | P95 ms | Peak MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical / balanced | 100.0% | 1.000 | 95.0% | 95.0% | 90.0% | 10.0% | 20.97 | 23.17 | 0.03 |
| bm25 / balanced | 100.0% | 1.000 | 71.4% | 100.0% | 20.0% | 80.0% | 22.00 | 31.77 | 0.03 |
| adaptive / survival | 100.0% | 1.000 | 95.0% | 95.0% | 90.0% | 10.0% | 19.75 | 22.28 | 0.03 |
| adaptive / balanced | 100.0% | 1.000 | 71.4% | 100.0% | 20.0% | 80.0% | 43.78 | 72.91 | 0.03 |
| adaptive / accuracy | 100.0% | 1.000 | 71.4% | 100.0% | 20.0% | 80.0% | 68.01 | 74.72 | 0.46 |
| adaptive / balanced / 0.4 mWh | 100.0% | 1.000 | 95.0% | 95.0% | 90.0% | 10.0% | 62.01 | 71.29 | 0.03 |
| adaptive / balanced / 64 MiB | 100.0% | 1.000 | 95.0% | 95.0% | 90.0% | 10.0% | 62.12 | 69.58 | 0.03 |

The meaningful result is not just perfect document ranking on this compact corpus. Lexical retrieval has substantially better refusal calibration here; BM25 and balanced adaptive retrieval incorrectly accept 8 of 10 unanswerable prompts. That is a useful safety regression target for LastLight. Answer precision includes the accept/refuse boundary, while Top-1 and MRR do not. The metrics deliberately expose that distinction.

The committed [`results/baseline.json`](results/baseline.json) contains raw per-case outcomes, environment metadata, planner decisions, timings, and slices by difficulty, language, category, and tag. Re-run it on target hardware before comparing efficiency.

## What is tested

The field-operations pack contains 10 substantial documents and more than 5,000 words in English and Spanish. Each manual has operational sections, decision branches, numeric constraints, warnings, handoffs, and plausible distractor language. The 30 labeled cases comprise 20 answerable queries and 10 expected refusals:

- direct lookup, paraphrase, numeric, and negative constraints;
- multi-condition and multi-step questions;
- English and Spanish retrieval in one mixed-language pack;
- high-risk medical and infrastructure wording;
- out-of-domain questions, including lexical distractors designed to tempt false acceptance.

This is a closed-corpus retrieval benchmark. It does not evaluate generative answer quality, factual correctness against real emergency standards, energy measured by physical instrumentation, or statistical generalization to arbitrary corpora.

## Metrics

| Metric | Definition |
|---|---|
| Top-1 accuracy | Answerable cases whose labeled document is ranked first / all answerable cases. |
| MRR | Mean reciprocal rank of the labeled document across answerable cases. |
| Answer precision | Accepted cases that are answerable and rank the labeled document first / all accepted cases. |
| Answerable recall | Correctly accepted answerable cases / all answerable cases. |
| Refusal recall | Refused unanswerable cases / all unanswerable cases. |
| False-accept rate | Accepted unanswerable cases / all unanswerable cases. |
| Latency | Wall-clock duration of `LastLight.query`, after warm-up; mean and interpolated P95. |
| Peak MiB | Maximum Python allocation peak from `tracemalloc` for one query; not process RSS. |

Lexical and BM25 scores are strategy-specific and are not directly compared. No composite score hides trade-offs. Raw cases remain available for error analysis.

## Reproduce

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
lastlight-bench-suite --output results/local.json
```

Or run a focused condition:

```bash
lastlight-bench --strategy adaptive --mode survival --output results/survival.json
lastlight-bench --strategy adaptive --energy-budget-mwh 0.4 --output results/low-energy.json
```

The full suite covers lexical, BM25, all three adaptive modes, an explicit 0.4 mWh/query policy budget, and a 64 MiB memory policy budget. These budget values test planner behavior; the harness does not claim to measure physical energy consumption.

## Corpus and ground truth

[`corpus/field-ops-v1`](corpus/field-ops-v1) is a LastLight Pack Format v1 directory. [`datasets/eval.jsonl`](datasets/eval.jsonl) is reviewable JSONL: every case carries an ID, query, language, category, answerability label, expected path, difficulty, and tags. Corpus prose and labels are versioned separately from code so changes produce an explicit benchmark diff.

Synthetic data makes the suite redistributable and deterministic but limits external validity. A production evaluation should add independently authored, subject-matter-reviewed documents and blind labels without silently mixing them into this baseline.

## Interpreting and extending results

Treat a change in corpus, labels, LastLight version, Python version, OS, processor, or harness as a new experimental condition. Do not compare latency across hosts as if controlled. For timing work, run repeated processes on an idle target device and report dispersion; for energy work, add an external power meter and sampling protocol.

New cases should be challenging for a stated reason, have one auditable expected document (or an explicit refusal label), avoid leaking filenames into queries, and pass schema checks. Never replace an unfavorable result with an easier query: add a versioned correction and explain it.

## CI quality gates

Pull requests run unit and integration tests on Python 3.10–3.12, execute the seven-condition matrix on Python 3.12, retain the raw artifact, and enforce conservative deterministic floors: Top-1 and MRR ≥ 0.95, answer precision ≥ 0.65, answerable recall ≥ 0.90, and refusal recall ≥ 0.20. Latency is reported but deliberately not gated on shared CI hardware. Tightening calibration thresholds is a versioned benchmark decision.

## Repository layout

```text
corpus/                 synthetic LastLight knowledge pack
datasets/eval.jsonl     labeled queries and refusal cases
src/lastlight_bench/    runner, metrics, slicing, and CLI
results/baseline.json   reproducible raw baseline artifact
tests/                  schema, metric, corpus, and smoke checks
```

## License

Mozilla Public License 2.0. The synthetic corpus is marked CC0-1.0 in its pack manifest.
