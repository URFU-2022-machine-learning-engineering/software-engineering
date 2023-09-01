import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, status

from api.spec.transcribe import TranscribeRequest, TranscribeResponse
from model import WhisperTranscriber

logger = logging.getLogger(name=__name__)
router = APIRouter()

dotenv_path = Path(".env.local")
load_dotenv(dotenv_path=dotenv_path)

model_name = "medium"
minio_endpoint = os.getenv("MINIO_ENDPOINT")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_use_ssl = bool(int(os.getenv("MINIO_USE_SSL")))

logger.debug(f"minio_endpoint: {minio_endpoint}, use ssl is {minio_use_ssl}")


@router.post("/transcribe", response_model=TranscribeResponse, status_code=status.HTTP_200_OK)
def transcribe(req: TranscribeRequest) -> TranscribeResponse | None:
    logger.debug(f"Received request {req}")
    try:
        logger.info("Initialize WT")
        whisper = WhisperTranscriber(
            model_name=model_name,
            minio_endpoint=minio_endpoint,
            minio_access_key=minio_access_key,
            minio_secret_key=minio_secret_key,
            minio_bucket=req.bucket,
            minio_use_ssl=minio_use_ssl,
        )
    except TypeError as err:
        logger.error(f"Could not initialize WT. Error was: {err}")
        return
    language, text = whisper.transcribe_audio(object_name=req.file_name)

    return TranscribeResponse(detected_language=language, recognized_text=text)
