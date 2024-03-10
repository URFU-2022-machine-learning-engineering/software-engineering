import logging
import os
from opentelemetry import trace
from fastapi import APIRouter, status
from api.spec.transcribe import TranscribeRequest, TranscribeResponse
from model import WhisperTranscriber

# Assuming the tracer has been initialized as shown in the first code snippet
tracer = trace.get_tracer(__name__)

router = APIRouter()

model_name = "medium"
minio_endpoint = os.getenv("MINIO_ENDPOINT")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_use_ssl = bool(int(os.getenv("MINIO_USE_SSL"))) if os.getenv("MINIO_USE_SSL") else True

logging.debug(f"minio_endpoint: {minio_endpoint}, use ssl is {minio_use_ssl}")


@tracer.start_as_current_span("transcribe")
@router.post("/transcribe", response_model=TranscribeResponse, status_code=status.HTTP_200_OK)
def transcribe(req: TranscribeRequest) -> TranscribeResponse | None:
    logging.debug(f"Received request {req}")
    try:
        logging.info("Initialize WhisperTranscriber")
        whisper = WhisperTranscriber(
            model_name=model_name,
            minio_endpoint=minio_endpoint,
            minio_access_key=minio_access_key,
            minio_secret_key=minio_secret_key,
            minio_bucket=req.bucket,
            minio_use_ssl=minio_use_ssl,
        )
    except TypeError as err:
        logging.error(f"Could not initialize WhisperTranscriber. Error was: {err}")
        return
    try:
        language, text = whisper.transcribe_audio(object_name=req.file_name)
    except Exception as e:
        logging.error(f"Could not transcribe audio. Error was: {e}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return TranscribeResponse(detected_language=language, recognized_text=text)
