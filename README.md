# LastLight Bench

[![CI](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/lastlight-bench/actions/workflows/ci.yml)

An auditable benchmark of [LastLight](https://github.com/edujbarrios/lastlight), the dependency-free offline retrieval library for degraded-infrastructure scenarios. It measures retrieval, answer/refusal calibration, latency, Python allocation peaks, multilingual routing, and adaptive policy selection through LastLight's public API.

> [!CAUTION]
> **The corpus and every evaluation question were invented by ChatGPT.** They simulate the content, structure, ambiguity, and operational language of a realistic municipal emergency-operations document set. They do not describe a real organization, are not expert-validated, and must never be used as medical, public-health, electrical, food-safety, or emergency guidance.

## Baseline results

Measured on LastLight 0.2.1 / Python 3.12 / Windows 11, with 60 cases, `top_k=3`, and three warm-up queries. Latency and allocation numbers are single-host observations, not universal product claims. Accuracy is deterministic for the pinned corpus and package version.

| Strategy / mode | Top-1 | MRR | Answer precision | Answerable recall | Refusal recall | False accept | Mean ms | P95 ms | Peak MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical / balanced | 90.0% | 0.950 | 74.5% | 87.5% | 55.0% | 45.0% | 19.69 | 23.26 | 0.44 |
| bm25 / balanced | 90.0% | 0.946 | 62.1% | 90.0% | 10.0% | 90.0% | 20.48 | 32.42 | 0.04 |
| adaptive / survival | 90.0% | 0.950 | 74.5% | 87.5% | 55.0% | 45.0% | 17.91 | 20.37 | 0.04 |
| adaptive / balanced | 90.0% | 0.950 | 62.1% | 90.0% | 10.0% | 90.0% | 21.32 | 32.13 | 0.04 |
| adaptive / accuracy | 90.0% | 0.946 | 62.1% | 90.0% | 10.0% | 90.0% | 19.76 | 21.98 | 0.83 |
| adaptive / balanced / 0.4 mWh | 90.0% | 0.950 | 74.5% | 87.5% | 55.0% | 45.0% | 18.43 | 20.77 | 0.44 |
| adaptive / balanced / 64 MiB | 90.0% | 0.950 | 74.5% | 87.5% | 55.0% | 45.0% | 17.97 | 19.76 | 0.04 |

The expanded corpus removes the unrealistically perfect retrieval result. All configurations reach 90% Top-1, with errors concentrated in manuals that deliberately share vocabulary and workflows. Lexical/survival policies refuse more unsupported questions, while BM25 and accuracy-oriented adaptive policies accept 18 of 20 unanswerable prompts. Ten of those prompts are difficult in-domain negatives: they mention real corpus topics but ask for absent live values, credentials, identities, legal thresholds, or clinical prescriptions. This exposes a concrete calibration weakness rather than hiding it behind an aggregate score.

The committed [`results/baseline.json`](results/baseline.json) contains raw per-case outcomes, environment metadata, planner decisions, timings, and slices by difficulty, language, category, and tag. Re-run it on target hardware before comparing efficiency.

## What is tested

The field-operations pack contains 16 substantial documents and more than 8,000 words in English and Spanish. Each manual has operational sections, decision branches, numeric constraints, warnings, handoffs, and plausible distractor language. Closely related manuals intentionally overlap—for example water advisory/flushing/chlorination, generator/electrical/fuel, radio/satellite, shelter intake/sanitation, and multiple medical protocols. The 60 labeled cases comprise 40 answerable queries and 20 expected refusals:

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

Pull requests run unit and integration tests on Python 3.10–3.12, execute the seven-condition matrix on Python 3.12, retain the raw artifact, and enforce deterministic regression floors fitted to corpus v1.1: Top-1 ≥ 0.85, MRR ≥ 0.90, answer precision ≥ 0.60, answerable recall ≥ 0.85, and refusal recall ≥ 0.10. These are regression floors, not quality targets; the measured refusal behavior shows why future releases should raise them. Latency is reported but deliberately not gated on shared CI hardware.

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
