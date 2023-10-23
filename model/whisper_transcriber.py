import logging

import whisper

from api.spec.transcribe import WhisperModels
from connectors import remove_temp_file, save_temp_file
from connectors.minio_connector import MinioClient


class WhisperTranscriber:
    def __init__(self, model_name: str):
        self.model = whisper.load_model(model_name)

    def transcribe_audio_file(self, audio_file_path: str) -> tuple[str, str] | None:
        try:
            logging.info("Starting transcription...")
            result = self.model.transcribe(audio_file_path, fp16=False, verbose=True)
            return result["language"], result["text"]
        except Exception as e:
            logging.error(f"Could not transcribe the file error: {e}")
            return


if __name__ == "__main__":
    import settings

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    minio_client = MinioClient(
        minio_endpoint=settings.MINIO_ENDPOINT,
        minio_access_key=settings.MINIO_ACCESS_KEY,
        minio_secret_key=settings.MINIO_SECRET_KEY,
        minio_bucket=settings.MINIO_BUCKET,
        minio_use_ssl=settings.MINIO_USE_SSL,
    )

    transcriber = WhisperTranscriber(model_name=WhisperModels.large_v2)
    audio_file = save_temp_file(minio_client.get_object("audio.mp3"))
    language, text = transcriber.transcribe_audio_file(audio_file_path=audio_file)
    remove_temp_file(audio_file)

    logging.info(f"Detected language: {language}")
    logging.info(f"Recognized text: {text}")
