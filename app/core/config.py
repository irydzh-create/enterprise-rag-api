import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Enterprise RAG API"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# Создаем объект настроек, который будем импортировать в другие файлы
settings = Settings()