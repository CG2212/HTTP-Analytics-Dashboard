import os

TARGET_URL = "https://httpbin.org"
MAX_SESSIONS_HISTORY = 50

# PostgreSQL Connection Credentials
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "http_analytics")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"