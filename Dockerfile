# Basis-Image mit schlankem Python 3.11 / Базовый легковесный образ Python 3.11
FROM python:3.11-slim

# Arbeitsverzeichnis im Container festlegen / Рабочая директория внутри контейнера
WORKDIR /app

# Systemabhaengigkeiten fuer C-Kompilierung installieren / Системные зависимости для сборки библиотек
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Abhaengigkeiten kopieren und installieren / Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungsquellcode kopieren / Копирование исходного кода проекта
COPY app/ ./app/
COPY main.py .

# Port fuer FastAPI freigeben / Порт для FastAPI
EXPOSE 8000

# Server ueber Uvicorn starten / Запуск сервера через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]