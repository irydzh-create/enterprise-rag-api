import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vector_store import get_vector_store


def ingest_documents():
    # Путь к папке с книгами / Pfad zum Ordner mit Büchern
    data_dir = "data/docs"

    # Проверка существования директории / Überprüfung der Existenz des Verzeichnisses
    if not os.path.exists(data_dir):
        print(f"Папка {data_dir} не найдена / Ordner {data_dir} nicht gefunden")
        return

    # Загрузка PDF из папки / Laden von PDFs aus dem Ordner
    print(f"Чтение документов из {data_dir}... / Lesen von Dokumenten aus {data_dir}...")
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()

    # Проверка наличия данных / Überprüfung auf vorhandene Daten
    if not documents:
        print("PDF файлы не найдены / Keine PDF-Dateien gefunden")
        return

    print(f"Загружено страниц: {len(documents)} / Geladene Seiten: {len(documents)}")

    # Нарезка текста на фрагменты / Aufteilen des Textes in Fragmente
    print("Разделение текста... / Text aufteilen...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Создано фрагментов: {len(chunks)} / Erstellte Fragmente: {len(chunks)}")

    # Сохранение данных в ChromaDB / Speichern der Daten in ChromaDB
    print("Сохранение в базу данных... / Speichern in der Datenbank...")
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    print("Процесс завершен / Prozess abgeschlossen")


if __name__ == "__main__":
    ingest_documents()