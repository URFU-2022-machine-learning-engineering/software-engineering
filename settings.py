from decouple import config

DB_HOST = config("DB_HOST", default="127.0.0.1", cast=str)
DB_PORT = config("DB_PORT", default=5432, cast=int)
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD", cast=str)
MIGRATIONS_VERSION = config("MIGRATIONS_VERSION")


MINIO_ENDPOINT = config("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = config("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = config("MINIO_SECRET_KEY")
MINIO_BUCKET = config("MINIO_BUCKET", default="audio")
MINIO_USE_SSL = config("MINIO_USE_SSL", default=True, cast=bool)
