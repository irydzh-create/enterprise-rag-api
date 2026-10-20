import os
import sys
from sentence_transformers import CrossEncoder
from langchain_community.retrievers import BM25Retriever

# Projekt-Wurzelverzeichnis zum Pfad hinzufuegen / Добавление корня проекта в системный путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.vector_store import get_vector_store, BASE_DIR
from app.services.document_loader import load_and_split_documents

# Cache fuer Modelle / Кэш для моделей
_cached_reranker = None

# Reranker-Modell bei Bedarf initialisieren / Инициализация реранкера по требованию
def get_reranker():
    global _cached_reranker
    if _cached_reranker is None:
        _cached_reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _cached_reranker

# BM25-Retriever initialisieren / Инициализация BM25-поисковика
def get_bm25_retriever(vector_store):
    # Use the indexed chunks, not a second parse of the source PDFs.
    from langchain_core.documents import Document

    indexed = vector_store.get()
    texts = indexed.get("documents") or []
    metadata = indexed.get("metadatas") or [{} for _ in texts]
    if not texts:
        return None
    chunks = [
        Document(page_content=text, metadata=meta or {})
        for text, meta in zip(texts, metadata)
    ]
    retriever = BM25Retriever.from_documents(chunks)
    retriever.k = 15
    return retriever

# Hybride Suche mit Cross-Encoder Reranking / Гибридный поиск с точным реранкингом
def search_documents(query: str, top_k: int = 3, candidate_pool: int = 6):
    vector_store = get_vector_store()
    if not vector_store:
        return []

    # 1. Semantische Vektorsuche / 1. Векторный семантический поиск
    chroma_retriever = vector_store.as_retriever(search_kwargs={"k": candidate_pool})
    vector_docs = chroma_retriever.invoke(query)

    # 2. BM25-Schluesselwortsuche / 2. Поиск по ключевым словам BM25
    bm25_retriever = get_bm25_retriever(vector_store)
    bm25_docs = bm25_retriever.invoke(query) if bm25_retriever else []

    # 3. Zusammenfuehren und Duplikate entfernen / 3. Объединение кандидатов и удаление дубликатов
    combined_docs = vector_docs + bm25_docs
    unique_candidates = []
    seen_texts = set()
    for doc in combined_docs:
        if doc.page_content not in seen_texts:
            seen_texts.add(doc.page_content)
            unique_candidates.append(doc)

    if not unique_candidates:
        return []

    # 4. Re-Ranking ueber Cross-Encoder / 4. Точный скоринг через Cross-Encoder
    reranker = get_reranker()
    pairs = [[query, doc.page_content] for doc in unique_candidates]
    scores = reranker.predict(pairs)

    # Nach Relevanz sortieren / Сортировка по релевантности
    scored_docs = list(zip(unique_candidates, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return [doc for doc, score in scored_docs[:top_k]]

# Testblock / Блок тестирования
if __name__ == "__main__":
    test_query = "Conditional Statements"
    results = search_documents(test_query, top_k=3)
    for i, doc in enumerate(results):
        print(f"\n--- Treffer / Результат {i+1} ---")
        print(doc.page_content[:200])