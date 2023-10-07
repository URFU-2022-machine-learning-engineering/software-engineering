import logging
import os

from fastapi import APIRouter, status

from api.spec.transcribe import TranscribeRequest, TranscribeResponse
from connectors import remove_temp_file, save_temp_file
from connectors.minio_connector import MinioClient
from model import WhisperTranscriber

router = APIRouter()

model_name = "medium"
minio_endpoint = os.getenv("MINIO_ENDPOINT")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_use_ssl = bool(int(os.getenv("MINIO_USE_SSL"))) if os.getenv("MINIO_USE_SSL") else True


logging.debug(f"minio_endpoint: {minio_endpoint}, use ssl is {minio_use_ssl}")


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    status_code=status.HTTP_200_OK,
)
def transcribe(req: TranscribeRequest) -> TranscribeResponse | None:
    try:
        logging.debug(f"Received request {req}")

        with MinioClient(
            minio_endpoint=minio_endpoint,
            minio_access_key=minio_access_key,
            minio_secret_key=minio_secret_key,
            minio_bucket=req.bucket,
            minio_use_ssl=minio_use_ssl,
        ) as minio_client, WhisperTranscriber(model_name=model_name) as whisper:
            audio_file = save_temp_file(minio_client.get_object(object_name=req.file_name))
            language, text = whisper.transcribe_audio_file(audio_file_path=audio_file)

            return TranscribeResponse(detected_language=language, recognized_text=text)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return TranscribeResponse(detected_language=None, recognized_text=None)
    finally:
        if audio_file:
            remove_temp_file(audio_file)
