import os
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Dokumente laden und in Abschnitte aufteilen / Загрузка документов и разбивка на чанки
def load_and_split_documents(directory_path: str):
    # Pruefen, ob das Verzeichnis existiert / Проверка существования директории
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Verzeichnis nicht gefunden / Директория не найдена: {directory_path}")

    print(f"Scanne Verzeichnis / Сканирую папку: {directory_path}")

    # PDF-Dateien ueber PyMuPDF laden / Загрузка PDF через PyMuPDF
    loader = DirectoryLoader(
        directory_path,
        glob="*.pdf",
        loader_cls=PyMuPDFLoader
    )
    raw_documents = loader.load()
    print(f"Geladene Seiten / Загружено страниц: {len(raw_documents)}")

    # Text in semantische Abschnitte unterteilen / Нарезка текста на смысловые фрагменты
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_documents(raw_documents)
    print(f"Erstellte Chunks / Создано фрагментов: {len(chunks)}")
    return chunks

# Testblock / Блок тестирования
if __name__ == "__main__":
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/docs'))
    chunks = load_and_split_documents(docs_dir)
    if chunks:
        print(f"Beispiel-Chunk / Пример чанка:\n{chunks[0].page_content[:200]}...")