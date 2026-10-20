"""Runtime settings shared by the API, ingestion and Telegram bot."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "Enterprise RAG API"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


settings = Settings()
