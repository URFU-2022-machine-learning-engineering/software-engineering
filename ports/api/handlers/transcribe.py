import logging

from fastapi import APIRouter, HTTPException, status
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode

from core import (
    WhisperTranscriber,
    minio_access_key,
    minio_endpoint,
    minio_secret_key,
    minio_use_ssl,
    model_name,
)
from ports.api.spec.transcribe import TranscribeRequest, TranscribeResponse

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"MinIO endpoint: {minio_endpoint}, use SSL is {minio_use_ssl}")


@router.post("/transcribe", response_model=TranscribeResponse, status_code=status.HTTP_200_OK)
async def transcribe(req: TranscribeRequest) -> TranscribeResponse:
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("transcribe") as span:
        logger.info(f"Received transcription request: {req}")

        try:
            whisper = WhisperTranscriber(
                model_name=model_name,
                minio_endpoint=minio_endpoint,
                minio_access_key=minio_access_key,
                minio_secret_key=minio_secret_key,
                minio_bucket=req.bucket,
                minio_use_ssl=minio_use_ssl,
            )
        except Exception as err:  # Using a broad exception catch to handle all potential initialization errors.
            span.record_exception(err)
            span.set_status(Status(StatusCode.ERROR, description=str(err)))
            logger.error(f"Initialization error in WhisperTranscriber: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error initializing the transcription service")

        try:
            language, text = whisper.transcribe_audio(object_name=req.file_name)
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, description=str(e)))
            logger.error(f"Transcription error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during audio transcription")

        # Successfully transcribed
        return TranscribeResponse(detected_language=language, recognized_text=text)
