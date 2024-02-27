import logging
import os
import tempfile

import whisper
from minio import Minio


class WhisperTranscriber:
    def __init__(
        self,
        model_name: str,
        minio_endpoint: str,
        minio_access_key: str,
        minio_secret_key: str,
        minio_bucket: str,
        minio_use_ssl: bool | str,
    ):
        self.model_name = model_name
        self.model = self.model_load()
        self.minio_client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_use_ssl,
        )
        self.bucket = minio_bucket

    def model_load(self):
        logging.info("Load model")
        return whisper.load_model(self.model_name)

    def transcribe_audio(self, object_name: str) -> tuple[str, str]:
        temp_file_path = self._get_file_from_minio(object_name)
        try:
            logging.info("Start transcription")
            result = self.model.transcribe(temp_file_path, fp16=False)
        finally:
            os.remove(temp_file_path)
            logging.info("Removed temp file")
        return result["language"], result["text"]

    def _get_file_from_minio(self, object_name: str) -> str | None:
        logging.info("get object from S3")
        try:
            object_data = self.minio_client.get_object(self.bucket, object_name)

            logging.debug("read object data into memory")
            object_bytes = object_data.data
        except Exception as e:
            logging.error(f"Could not get object from S3. Error was: {e}")
            return
        else:
            logging.debug("Successfully read object data into memory")
            object_data.close()
        finally:
            object_data.release_conn()

        logging.debug("Create a temporary file and write the object bytes")
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(object_bytes)
            temp_file_path = temp_file.name
            return temp_file_path


if __name__ == "__main__":
    from pathlib import Path

    from dotenv import load_dotenv

    dotenv_path = Path("/var/whisper/.env.local")
    load_dotenv(dotenv_path=dotenv_path)

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    transcriber = WhisperTranscriber(
        model_name="large",
        minio_endpoint=os.getenv("MINIO_ENDPOINT"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY"),
        minio_bucket=os.getenv("MINIO_BUCKET"),
        minio_use_ssl=bool(int(os.getenv("MINIO_USE_SSL"))),
    )

    language, text = transcriber.transcribe_audio("audio.mp3")
    logging.info(f"Detected language: {language}")
    logging.info(f"Recognized text: {text}")
