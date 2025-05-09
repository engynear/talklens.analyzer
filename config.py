import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "telegram-messages")

# Batching settings
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))
BATCH_TIMEOUT_SECONDS = int(os.getenv("BATCH_TIMEOUT_SECONDS", "30"))

# LLM settings
USE_API = os.getenv("USE_API", "false").lower() == "true"
API_URL = os.getenv("API_URL", "")
API_KEY = os.getenv("API_KEY", "")
# Настройки для YandexGPT
YANDEX_API = os.getenv("YANDEX_API", "false").lower() == "true"
FOLDER_ID = os.getenv("FOLDER_ID", "")

# Database settings - используем стандартные переменные Postgres
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "talklens")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
