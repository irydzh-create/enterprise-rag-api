import os
from dotenv import load_dotenv

# # Load environment variables from .env file / Загружаем переменные из файла .env
load_dotenv()

class Settings:
    # # Project configuration / Конфигурация проекта
    PROJECT_NAME: str = "Enterprise RAG API"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# # Create settings instance for import / Создаем объект настроек для импорта в другие файлы
settings = Settings()