"""Build deterministic retrieval cases from the pinned medicine-pack slice."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "official-medicines-es-it"
OUTPUT = ROOT / "datasets" / "eval.jsonl"

SYMPTOMS = {
    "acid-disorders": ("ardor de estómago", "bruciore di stomaco"),
    "analgesics": ("dolor de cabeza", "mal di testa"),
    "antibacterials": ("dolor de garganta y fiebre", "mal di gola e febbre"),
    "antidiabetics": ("mucha sed y cansancio", "molta sete e stanchezza"),
    "antiinflammatories": ("dolor e inflamación de rodilla", "dolore e gonfiore al ginocchio"),
    "antithrombotics": ("una pierna hinchada", "una gamba gonfia"),
    "beta-blockers": ("palpitaciones", "palpitazioni"),
    "obstructive-airway": ("falta de aire", "fiato corto"),
    "psycholeptics": ("insomnio y ansiedad", "insonnia e ansia"),
    "systemic-corticosteroids": ("una erupción cutánea", "un'eruzione cutanea"),
}


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
                (
                    f"Antes de valorar {medicine}, necesito contrastar en su ficha oficial sus "
                    "indicaciones, contraindicaciones, interacciones y precauciones en poblaciones "
                    "especiales. ¿Qué documento del paquete reúne esa información?",
                    "multi-section",
                    "prospectus-safety",
                ),
            )
        else:
            facts = (
                (f"Qual è il principio attivo di {medicine}?", "direct", "active-ingredient"),
                (
                    f"Prima di valutare {medicine}, devo confrontare nella scheda ufficiale "
                    "indicazioni, controindicazioni, interazioni e precauzioni per popolazioni "
                    "speciali. Quale documento del pacchetto contiene queste informazioni?",
                    "multi-section",
                    "prospectus-safety",
                ),
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

    curated_scenarios = (
        {
            "id": "es-answerable-scenario-001",
            "query": (
                "Una persona menor de 16 años con cefalea usa metotrexato a 15 mg por semana. "
                "¿Qué ficha del paquete corresponde al medicamento que combina ácido "
                "acetilsalicílico, paracetamol y cafeína y obliga a revisar ambos riesgos?"
            ),
            "language": "es",
            "expected_path": (
                "es/analgesics/47178-actron-compuesto-267-mg-133-mg-40-mg-"
                "comprimidos-efervescentes.md"
            ),
        },
        {
            "id": "it-answerable-scenario-001",
            "query": (
                "Un adulto con mal di testa assume warfarin e metotrexato a 15 mg/settimana. "
                "Quale scheda del pacchetto descrive compresse da 500 mg di acido "
                "acetilsalicilico e riporta entrambe le interazioni come controindicazioni?"
            ),
            "language": "it",
            "expected_path": "it/analgesics/004763-aspirina.md",
        },
    )
    for scenario in curated_scenarios:
        add_case(
            cases,
            **scenario,
            category="analgesics",
            answerable=True,
            difficulty="clinical-scenario",
            tags=["symptom", "contraindication", "interaction", "multi-constraint"],
        )

    for language in ("es", "it"):
        categories = sorted({case["category"] for case in cases if case["language"] == language})
        for index, category in enumerate(categories, 1):
            symptom = SYMPTOMS[category][0 if language == "es" else 1]
            query = (
                f"Tengo {symptom}, pero no he indicado mi edad, antecedentes, alergias ni otros "
                "tratamientos. ¿Qué medicamento exacto del paquete y qué dosis debo tomar?"
                if language == "es"
                else f"Ho {symptom}, ma non ho indicato età, anamnesi, allergie o altre terapie. "
                "Quale medicinale esatto del pacchetto e quale dose devo assumere?"
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
                tags=["symptom", "personalized-treatment", "insufficient-context", category],
            )

    OUTPUT.write_text(
        "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases),
        encoding="utf-8",
    )
    print(f"wrote {len(cases)} cases to {OUTPUT}")


if __name__ == "__main__":
    main()
