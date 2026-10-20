"""Real PDF parsing + persistent Chroma, with deterministic local embeddings."""
import fitz
import pytest
from langchain_core.embeddings import Embeddings

import ingest
from app.services import vector_store


class TinyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[1.0, float(len(text) % 17) / 17, 0.5] for text in texts]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def write_pdf(path, text):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(str(path))
    document.close()


def test_pdf_first_run_repeat_and_changed_source(tmp_path, monkeypatch):
    docs = tmp_path / "data" / "docs"
    docs.mkdir(parents=True)
    pdf = docs / "example.PDF"
    write_pdf(pdf, "Original Python documentation.")
    monkeypatch.setattr(ingest, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(vector_store, "CHROMA_PERSIST_DIR", str(tmp_path / "index"))
    monkeypatch.setattr(vector_store, "get_huggingface_embeddings", lambda: TinyEmbeddings())

    count = ingest.ingest_documents()
    store = vector_store.get_vector_store()
    first = store.get()
    assert count > 0
    assert len(first["ids"]) == count
    assert first["metadatas"][0]["source"] == "example.PDF"
    ingest.ingest_documents()
    assert set(store.get()["ids"]) == set(first["ids"])

    pdf.unlink()
    write_pdf(pdf, "Updated Python documentation with new details.")
    ingest.ingest_documents()
    current = store.get()
    assert len(current["ids"]) == count
    assert set(current["ids"]).isdisjoint(first["ids"])
    assert "Updated" in current["documents"][0]

    pdf.unlink()
    with pytest.raises(ValueError, match="No PDF text"):
        ingest.ingest_documents()
    assert store.get()["ids"] == current["ids"]
