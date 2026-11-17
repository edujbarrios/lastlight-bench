"""Build deterministic retrieval cases from the pinned medicine-pack slice."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "official-medicines-es-it"
OUTPUT = ROOT / "datasets" / "eval.jsonl"


def title(text: str) -> str:
    match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    if not match:
        raise ValueError("missing title")
    return match.group(1).strip()


def add_case(cases: list[dict], **case: object) -> None:
    cases.append(case)


def main() -> None:
    cases: list[dict] = []
    counters = {"es": 0, "it": 0}
    groups: dict[tuple[str, str], list[Path]] = {}
    for path in sorted(CORPUS.rglob("*.md")):
        relative = path.relative_to(CORPUS).as_posix()
        language, category = relative.split("/", 2)[:2]
        groups.setdefault((language, category), []).append(path)

    sampled = [path for paths in groups.values() for path in paths[:2]]
    for path in sorted(sampled):
        relative = path.relative_to(CORPUS).as_posix()
        language, category = relative.split("/", 2)[:2]
        text = path.read_text(encoding="utf-8")
        medicine = title(text)
        if language == "es":
            facts = (
                (f"¿Cuál es el principio activo de {medicine}?", "direct", "active-ingredient"),
            )
        else:
            facts = (
                (f"Qual è il principio attivo di {medicine}?", "direct", "active-ingredient"),
            )
        for query, difficulty, tag in facts:
            counters[language] += 1
            add_case(
                cases,
                id=f"{language}-answerable-{counters[language]:03d}",
                query=query,
                language=language,
                category=category,
                answerable=True,
                expected_path=relative,
                difficulty=difficulty,
                tags=[tag, "official-source"],
            )

    for language in ("es", "it"):
        categories = sorted({case["category"] for case in cases if case["language"] == language})
        for index, category in enumerate(categories, 1):
            query = (
                f"¿Qué farmacia tiene hoy existencias y qué dosis debo tomar de MEDICAMENTO INEXISTENTE {index}?"
                if language == "es"
                else f"Quale farmacia ha disponibilità oggi e quale dose devo assumere di MEDICINALE INESISTENTE {index}?"
            )
            add_case(
                cases,
                id=f"{language}-unanswerable-{index:03d}",
                query=query,
                language=language,
                category="unanswerable-in-domain",
                answerable=False,
                expected_path=None,
                difficulty="hard-negative",
                tags=["live-state", "prescription", category],
            )

    OUTPUT.write_text(
        "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases),
        encoding="utf-8",
    )
    print(f"wrote {len(cases)} cases to {OUTPUT}")


if __name__ == "__main__":
    main()
