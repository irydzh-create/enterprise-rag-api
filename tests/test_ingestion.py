import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document
from ingest import ingest_documents
from app.services.retriever import get_bm25_retriever


@patch("ingest.create_vector_store")
@patch("ingest.load_and_split_documents")
def test_ingestion_creates_store_and_uses_stable_ids(load, create):
    create.return_value.get.return_value = {"ids": []}
    load.return_value = [
        Document(page_content="Example text", metadata={"source": "test.pdf", "page": 0})
    ]
    assert ingest_documents() == 1
    first_ids = create.call_args.kwargs["ids"]
    ingest_documents()
    assert create.call_args.kwargs["ids"] == first_ids
    assert len(first_ids) == 1


@patch("ingest.create_vector_store")
@patch("ingest.load_and_split_documents", return_value=[])
def test_empty_ingestion_does_not_create_store(load, create):
    with pytest.raises(ValueError, match="No PDF text"):
        ingest_documents()
    create.assert_not_called()


def test_bm25_reads_current_index_without_source_pdfs():
    store = Mock()
    store.get.return_value = {
        "documents": ["alpha document", "beta document"],
        "metadatas": [{"page": 0}, {"page": 1}],
    }
    retriever = get_bm25_retriever(store)
    assert {doc.page_content for doc in retriever.invoke("alpha")} == {
        "alpha document", "beta document",
    }
    store.get.return_value = {"documents": ["new document"], "metadatas": [None]}
    retriever = get_bm25_retriever(store)
    assert retriever.invoke("new")[0].page_content == "new document"


def test_empty_index_has_no_bm25_retriever():
    store = Mock()
    store.get.return_value = {"documents": [], "metadatas": []}
    assert get_bm25_retriever(store) is None
