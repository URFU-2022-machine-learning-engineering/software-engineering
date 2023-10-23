import logging

from fastapi import APIRouter, Response, status

import settings
from api.spec.transcribe import TranscribeRequest, TranscribeResponse, WhisperModels
from connectors import remove_temp_file, save_temp_file
from connectors.minio_connector import MinioClient
from model import WhisperTranscriber

router = APIRouter()


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    status_code=status.HTTP_200_OK,
)
def transcribe(req: TranscribeRequest, response: Response) -> TranscribeResponse | None:
    audio_file = None
    logging.debug(f"minio_endpoint: {settings.MINIO_ENDPOINT}, use ssl is {settings.MINIO_USE_SSL}")
    try:
        logging.debug(f"Received request {req}")
        minio_client = MinioClient(
            minio_endpoint=settings.MINIO_ENDPOINT,
            minio_access_key=settings.MINIO_ACCESS_KEY,
            minio_secret_key=settings.MINIO_SECRET_KEY,
            minio_bucket=req.bucket,
            minio_use_ssl=settings.MINIO_USE_SSL,
        )

        whisper = WhisperTranscriber(model_name=req.model if req.model else WhisperModels.medium)
        audio_file = save_temp_file(minio_client.get_object(object_name=req.file_name))
        language, text = whisper.transcribe_audio_file(audio_file_path=audio_file)

        return TranscribeResponse(detected_language=language, recognized_text=text)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return TranscribeResponse(detected_language="", recognized_text="")
    finally:
        if audio_file:
            remove_temp_file(audio_file)
            logging.info(f"{audio_file} has been removed")
        else:
            logging.error("There is no saved audio_file")
