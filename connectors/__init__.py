import logging
import os
import tempfile


def remove_temp_file(temp_file_path: str):
    try:
        logging.info(f"Removing file {temp_file_path}")
        os.remove(path=temp_file_path)
    except OSError as e:
        logging.error(f"Couldn't remove the file {temp_file_path}, error: {e}")


def save_temp_file(audio_bytes: bytes, prefix: str) -> str:
    logging.debug("Create a temporary file and write the audio bytes")

    with tempfile.NamedTemporaryFile(delete=False, prefix=f"{prefix}_") as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
        return temp_file_path
