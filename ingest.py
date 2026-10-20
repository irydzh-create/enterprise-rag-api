"""Index PDFs using the same chunks consumed by hybrid retrieval."""
import hashlib
import json
import os

from app.services.document_loader import load_and_split_documents
from app.services.vector_store import BASE_DIR, create_vector_store


def ingest_documents():
    data_dir = os.path.join(BASE_DIR, "data", "docs")
    chunks = load_and_split_documents(data_dir)
    if not chunks:
        print("No PDF text found in data/docs.")
        return 0
    # Stable IDs make re-indexing unchanged PDFs idempotent.
    ids = [
        hashlib.sha256(
            json.dumps(
                {"text": doc.page_content, "metadata": doc.metadata},
                sort_keys=True, ensure_ascii=False, default=str,
            ).encode("utf-8")
        ).hexdigest()
        for doc in chunks
    ]
    unique = dict(zip(ids, chunks))
    create_vector_store(list(unique.values()), ids=list(unique))
    print(f"Indexed {len(unique)} chunks.")
    return len(unique)


if __name__ == "__main__":
    ingest_documents()
