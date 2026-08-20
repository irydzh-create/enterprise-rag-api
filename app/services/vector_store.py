import os
import sys

# Добавляем корневую папку проекта в пути Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.services.document_loader import load_documents

# 🎯 АБСОЛЮТНЫЙ ПУТЬ к базе данных (теперь работает из ЛЮБОЙ папки!)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "chroma_db")


def get_huggingface_embeddings():
    """
    Загружает бесплатную локальную модель для создания векторов.
    """
    return HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")


def create_vector_store(documents):
    """
    Создает векторы из документов и сохраняет их в локальную БД Chroma.
    """
    embeddings = get_huggingface_embeddings()

    print("Создаю векторы локально (HuggingFace) и сохраняю в базу данных (Chroma)...")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

    print(f"✅ База данных успешно создана и сохранена в: {CHROMA_PERSIST_DIR}")
    return vector_store


def get_vector_store():
    """
    Загружает существующую базу данных для поиска.
    """
    if not os.path.exists(CHROMA_PERSIST_DIR):
        print(f"❌ База данных не найдена по пути: {CHROMA_PERSIST_DIR}")
        return None

    embeddings = get_huggingface_embeddings()

    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    return vector_store


# === БЛОК ЗАПУСКА ===
if __name__ == "__main__":
    docs_dir = os.path.join(BASE_DIR, "data", "docs")

    print("Начинаем обработку документов...")
    documents = load_documents(docs_dir)

    if documents:
        create_vector_store(documents)
    else:
        print("Внимание: Документы не найдены. Проверьте, лежат ли PDF в папке data/docs")