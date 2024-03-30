import logging

# Configuration variables
import os

from .whisper_transcriber import WhisperTranscriber

logger = logging.getLogger(__name__)

model_name = os.getenv("MODEL_NAME")
minio_endpoint = os.getenv("MINIO_ENDPOINT")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_use_ssl = os.getenv("MINIO_USE_SSL", "true").lower() in ("true", "1", "t")


if model_name == "":
    model_name = "large"
    logger.warning("MODEL_NAME is not set using large")

if minio_endpoint == "":
    logger.error("MINIO_ENDPOINT is not set")
    raise ValueError("MINIO_ENDPOINT is not set")

if minio_access_key == "":
    logger.error("MINIO_ACCESS_KEY is not set")
    raise ValueError("MINIO_ACCESS_KEY is not set")

if minio_secret_key == "":
    logger.error("MINIO_SECRET_KEY is not set")
    raise ValueError("MINIO_SECRET_KEY is not set")

if minio_use_ssl == "":
    minio_use_ssl = True
    logger.warning("MINIO_USE_SSL is not set using True")
