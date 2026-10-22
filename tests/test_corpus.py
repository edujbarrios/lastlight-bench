from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "field-ops-v1"


def test_corpus_is_substantial_and_explicitly_synthetic() -> None:
    documents = list(CORPUS.rglob("*.md"))
    assert len(documents) == 16
    assert sum(len(path.read_text(encoding="utf-8").split()) for path in documents) >= 8_000
    for document in documents:
        text = document.read_text(encoding="utf-8").lower()
        assert len(text.split()) >= 400, document
        assert "synthetic" in text or "sintético" in text, document


def test_manifest_declares_synthetic_source_and_languages() -> None:
    manifest = json.loads((CORPUS / "lastlight-pack.json").read_text(encoding="utf-8"))
    assert manifest["source"].startswith("synthetic://chatgpt/")
    assert manifest["languages"] == ["en", "es"]

