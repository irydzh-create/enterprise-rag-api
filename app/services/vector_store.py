import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Папка, где база данных будет хранить векторы
CHROMA_PERSIST_DIR = "../../data/chroma_db"


def get_huggingface_embeddings():
    """
    Загружает бесплатную локальную модель для создания векторов.
    При первом запуске она скачается на ваш компьютер (около 80 МБ).
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def create_vector_store(documents):
    """
    Создает векторы из документов и сохраняет их в локальную БД Chroma.
    """
    embeddings = get_huggingface_embeddings()

    print("Создаю векторы локально (HuggingFace) и сохраняю в базу данных (Chroma)...")

    # Создаем базу данных из переданных документов
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
        print("База данных не найдена. Сначала нужно загрузить документы.")
        return None

    embeddings = get_huggingface_embeddings()

    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    return vector_store