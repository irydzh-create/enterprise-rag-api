import os
import sys

# Projekt-Wurzelverzeichnis zum Pfad hinzufuegen / Добавление корня проекта в системный путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.services.document_loader import load_and_split_documents

# Pfade definieren / Определение путей
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Mehrsprachiges Embedding-Modell initialisieren / Инициализация мультиязычной модели эмбеддингов
def get_huggingface_embeddings():
    return HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

# Vektorspeicher erstellen und speichern / Создание и сохранение векторного хранилища
def create_vector_store(documents):
    embeddings = get_huggingface_embeddings()
    print("Erstelle Vektorspeicher / Создание векторного хранилища...")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

    print(f"Vektorspeicher gespeichert unter / Векторная база сохранена в: {CHROMA_PERSIST_DIR}")
    return vector_store

# Bestehenden Vektorspeicher abrufen / Получение существующей векторной базы
def get_vector_store():
    if not os.path.exists(CHROMA_PERSIST_DIR):
        print(f"Vektorspeicher nicht gefunden / Векторная база не найдена: {CHROMA_PERSIST_DIR}")
        return None

    embeddings = get_huggingface_embeddings()
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )

# Ausfuehrungsblock / Блок выполнения
if __name__ == "__main__":
    docs_dir = os.path.join(BASE_DIR, "data", "docs")
    print("Starte Dokumentenindizierung / Запуск индексации документов...")
    chunks = load_and_split_documents(docs_dir)

    if chunks:
        create_vector_store(chunks)
    else:
        print("Keine Dokumente in data/docs gefunden / Документы в data/docs не найдены")