"""Hybrid retrieval over one persisted corpus."""
from functools import lru_cache
from threading import Lock

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from app.services.vector_store import get_vector_store

_bm25_lock = Lock()
_bm25_signature = None
_bm25_retriever = None


@lru_cache(maxsize=1)
def get_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def get_bm25_retriever(vector_store):
    global _bm25_signature, _bm25_retriever
    indexed = vector_store.get()
    texts = indexed.get("documents") or []
    metadata = indexed.get("metadatas") or [{} for _ in texts]
    signature = tuple(
        (text, tuple(sorted((meta or {}).items())))
        for text, meta in zip(texts, metadata)
    )
    with _bm25_lock:
        if signature != _bm25_signature:
            documents = [
                Document(page_content=text, metadata=meta or {})
                for text, meta in zip(texts, metadata) if text and text.strip()
            ]
            _bm25_retriever = BM25Retriever.from_documents(documents) if documents else None
            if _bm25_retriever is not None:
                _bm25_retriever.k = 15
            _bm25_signature = signature
        return _bm25_retriever


def search_documents(query: str, top_k: int = 3, candidate_pool: int = 6):
    if top_k < 1 or candidate_pool < 1:
        raise ValueError("Retrieval limits must be positive.")
    vector_store = get_vector_store()
    if vector_store is None:
        return []
    vector_docs = vector_store.as_retriever(
        search_kwargs={"k": max(candidate_pool, top_k)}
    ).invoke(query)
    bm25 = get_bm25_retriever(vector_store)
    lexical_docs = bm25.invoke(query) if bm25 is not None else []
    candidates = {}
    for doc in vector_docs + lexical_docs:
        candidates.setdefault(doc.page_content, doc)
    documents = list(candidates.values())
    if not documents:
        return []
    scores = get_reranker().predict([[query, doc.page_content] for doc in documents])
    return [
        doc for doc, score in sorted(
            zip(documents, scores), key=lambda item: item[1], reverse=True
        )[:top_k]
    ]
