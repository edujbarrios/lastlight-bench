# LastLight Bench

[![CI](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml)

An auditable benchmark of [LastLight](https://github.com/edujbarrios/lastlight), the dependency-free offline retrieval library for degraded-infrastructure scenarios. It measures retrieval, answer/refusal calibration, latency, Python allocation peaks, multilingual routing, and adaptive policy selection through LastLight's public API.

> [!CAUTION]
> **The recommendations included in this corpus were produced by ChatGPT for benchmarking purposes.** In a real deployment, every statement in the source documents must be verified in advance and must follow the criteria, authority, and operating procedures of the organization responsible for them. Because those internal criteria are normally private, this repository uses a synthetic document set that only emulates how such operational guidance might be structured. This dataset must never be used for operational decision-making; it exists exclusively to evaluate the benchmark.

## Baseline results

Measured on LastLight 0.2.1 / Python 3.12 / Windows 11, with 120 cases, `top_k=3`, and three warm-up queries. Latency and allocation numbers are single-host observations, not universal product claims. Accuracy is deterministic for the pinned corpus and package version.

| Strategy / mode | Top-1 | MRR | Answer precision | Answerable recall | Refusal recall | False accept | Mean ms | P95 ms | Peak MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical / balanced | 81.2% | 0.885 | 64.0% | 80.0% | 42.5% | 57.5% | 79.45 | 134.34 | 0.45 |
| bm25 / balanced | 88.8% | 0.935 | 60.2% | 88.8% | 5.0% | 95.0% | 126.54 | 139.72 | 0.45 |
| adaptive / survival | 81.2% | 0.881 | 64.0% | 80.0% | 42.5% | 57.5% | 125.24 | 142.10 | 0.06 |
| adaptive / balanced | 86.2% | 0.927 | 59.0% | 86.2% | 7.5% | 92.5% | 133.14 | 161.88 | 0.45 |
| adaptive / accuracy | 88.8% | 0.935 | 60.2% | 88.8% | 5.0% | 95.0% | 130.51 | 155.62 | 1.18 |
| adaptive / balanced / 0.4 mWh | 81.2% | 0.881 | 64.0% | 80.0% | 42.5% | 57.5% | 126.09 | 142.55 | 0.06 |
| adaptive / balanced / 64 MiB | 81.2% | 0.881 | 64.0% | 80.0% | 42.5% | 57.5% | 122.84 | 132.32 | 0.45 |

The larger corpus produces a much more discriminating result. Top-1 ranges from 81.2% to 88.8%, with errors concentrated in manuals that deliberately share terminology and workflows. BM25 improves ranking and answerable recall, but accepts 38 of 40 unanswerable prompts; its 5% refusal recall and 95% false-accept rate show that ranking strength does not imply safe answer calibration. Lexical and survival policies reject more unsupported prompts, but still accept 23 of 40. Thirty refusal cases are difficult in-domain negatives: they mention genuine corpus topics while asking for absent live values, credentials, identities, authority decisions, or unsupported prescriptions.

The committed [`results/baseline.json`](results/baseline.json) contains raw per-case outcomes, environment metadata, planner decisions, timings, and slices by difficulty, language, category, and tag. Re-run it on target hardware before comparing efficiency.

## What is tested

The field-operations pack contains 24 substantial documents and more than 12,000 words in English and Spanish. Each manual has operational sections, decision branches, numeric constraints, warnings, handoffs, and plausible distractor language. Closely related manuals intentionally overlap—for example water advisory/flushing/pump/chlorination, generator/electrical/battery/fuel, radio/satellite/formal messages, shelter intake/sanitation/fire watch, and multiple medical protocols. The 120 labeled cases comprise 80 answerable queries and 40 expected refusals:

- direct lookup, paraphrase, numeric, and negative constraints;
- multi-condition and multi-step questions;
- English and Spanish retrieval in one mixed-language pack;
- high-risk medical and infrastructure wording;
- out-of-domain questions, including lexical distractors designed to tempt false acceptance.
- in-domain unanswerable questions requesting absent live state, credentials, identities, legal rules, or unsupported prescriptions.

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

Pull requests run unit and integration tests on Python 3.10–3.12, execute the seven-condition matrix on Python 3.12, retain the raw artifact, and enforce deterministic regression floors fitted to corpus v2.0: Top-1 ≥ 0.80, MRR ≥ 0.87, answer precision ≥ 0.58, answerable recall ≥ 0.78, and refusal recall ≥ 0.05. These are regression floors, not quality targets; the measured refusal behavior shows why future releases should raise them. Latency is reported but deliberately not gated on shared CI hardware.

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
