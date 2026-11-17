from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "official-medicines-es-it"


def test_corpus_has_ten_official_medicines_per_category_and_language() -> None:
    documents = list(CORPUS.rglob("*.md"))
    assert len(documents) == 200
    counts: dict[tuple[str, str], int] = {}
    for document in documents:
        language, category = document.relative_to(CORPUS).parts[:2]
        counts[(language, category)] = counts.get((language, category), 0) + 1
    assert set(language for language, _ in counts) == {"es", "it"}
    assert len(counts) == 20
    assert set(counts.values()) == {10}


def test_manifest_declares_official_sources_languages_and_provenance() -> None:
    manifest = json.loads((CORPUS / "lastlight-pack.json").read_text(encoding="utf-8"))
    assert "cima.aemps.es" in manifest["source"]
    assert "medicinali.aifa.gov.it" in manifest["source"]
    assert manifest["languages"] == ["es", "it"]
    assert manifest["version"] == "0.2.0"
    assert len(manifest["provenance"]) == 200

