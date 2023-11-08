from decouple import config

MINIO_ENDPOINT = config("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = config("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = config("MINIO_SECRET_KEY")
MINIO_BUCKET = config("MINIO_BUCKET", default="audio")
MINIO_USE_SSL = config("MINIO_USE_SSL", default=True, cast=bool)
