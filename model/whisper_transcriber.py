import logging
import os
import tempfile

import torch
import whisper
from minio import Minio

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


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
        self.model = whisper.load_model(model_name)
        self.minio_client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_use_ssl,
        )
        self.bucket = minio_bucket

    def transcribe_audio(self, object_name: str) -> tuple[str, str]:
        logging.debug("get log-Mel spectrogram from Minio")
        mel = self._get_log_mel_spectrogram(object_name)

        logging.debug("detect the spoken language")
        _, probs = self.model.detect_language(mel)
        language = max(probs, key=probs.get)

        logging.debug("decode the audio")
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(self.model, mel, options)
        logging.debug(f"return language {language} and {result.text}")
        return language, result.text

    def _get_log_mel_spectrogram(self, object_name: str) -> torch.Tensor:
        logging.debug("get object from Minio")
        try:
            object_data = self.minio_client.get_object(self.bucket, object_name)

            logging.debug("read object data into memory")
            object_bytes = object_data.data
        finally:
            object_data.close()
            object_data.release_conn()

        logging.debug("Create a temporary file and write the object bytes")
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(object_bytes)
            temp_file_path = temp_file.name

        logging.debug(" load audio and pad/trim it to fit 30 seconds")
        audio = whisper.load_audio(temp_file_path)
        audio = whisper.pad_or_trim(audio)

        logging.debug("make log-Mel spectrogram and move to the same device as the model")
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        logging.debug("Delete the temporary file")
        os.remove(temp_file_path)

        return mel


if __name__ == "__main__":
    from pathlib import Path

    from dotenv import load_dotenv

    dotenv_path = Path("../.env.local")
    load_dotenv(dotenv_path=dotenv_path)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    transcriber = WhisperTranscriber(
        model_name="large",
        minio_endpoint=os.getenv("MINIO_ENDPOINT"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY"),
        minio_bucket=os.getenv("MINIO_BUCKET"),
        minio_use_ssl=False,
    )

    language, text = transcriber.transcribe_audio("audio.mp3")
    logging.info(f"Detected language: {language}")
    logging.info(f"Recognized text: {text}")
