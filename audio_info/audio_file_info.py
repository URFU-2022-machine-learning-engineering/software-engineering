import logging
import os

import eyed3
from pydub import AudioSegment
from sqlalchemy import ARRAY, Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from connectors import save_temp_file
from connectors.minio_connector import MinioClient

Base = declarative_base()


class AudioInfo(Base):
    __tablename__ = "audio_info"

    id = Column(Integer, primary_key=True, unique=True)
    filename = Column(String)
    length = Column(Float)
    size = Column(Integer)
    bitrate = Column(Integer)
    samplerate = Column(Integer)
    mfccs = Column(ARRAY(Float))
    chroma = Column(ARRAY(Float))
    artist = Column(String)
    genre = Column(String)


def get_audio_info(file_path: str) -> dict:
    try:
        audio = AudioSegment.from_file(file_path)
        filename = os.path.basename(file_path)
        length = len(audio) / 1000  # Length in seconds
        size = os.path.getsize(file_path)  # Size in bytes
        bitrate = audio.frame_rate
        samplerate = audio.frame_rate

        # Extract MFCCs and Chroma features
        mfccs = audio.get_array_of_samples()
        chroma = audio.get_array_of_samples()

        # Example: Extract artist and genre (replace with your actual methods)
        artist = get_artist_from_metadata(file_path)
        genre = get_genre_from_metadata(file_path)

        return {
            "filename": filename,
            "length": length,
            "size": size,
            "bitrate": bitrate,
            "samplerate": samplerate,
            "mfccs": mfccs,
            "chroma": chroma,
            "artist": artist,
            "genre": genre,
        }
    except Exception as e:
        return {"error": str(e)}


# Example functions to extract artist and genre from metadata (replace with your actual methods)
def get_artist_from_metadata(file_path: str) -> str:
    try:
        audiofile = eyed3.load(file_path)
        if audiofile.tag.artist:
            return audiofile.tag.artist
        else:
            return "Unknown Artist"
    except Exception as e:
        logging.error(f"Error received while getting artist info {e}")
        return "Unknown Artist"


def get_genre_from_metadata(file_path: str) -> str:
    try:
        audiofile = eyed3.load(file_path)
        if audiofile.tag.genre:
            return audiofile.tag.genre.name
        else:
            return "Unknown Genre"
    except Exception as e:
        logging.error(f"Error received while getting genre info {e}")
        return "Unknown Genre"


def save_audio_info_to_db(audio_info):
    try:
        # TODO: Replace with database connection string
        engine = create_engine("postgresql://your_user:your_password@your_host/your_db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        audio_record = AudioInfo(
            filename=audio_info["filename"],
            length=audio_info["length"],
            size=audio_info["size"],
            bitrate=audio_info["bitrate"],
            samplerate=audio_info["samplerate"],
            mfccs=audio_info["mfccs"],
            chroma=audio_info["chroma"],
            artist=audio_info["artist"],
            genre=audio_info["genre"],
        )

        session.add(audio_record)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    from pathlib import Path

    from dotenv import load_dotenv

    dotenv_path = Path("../.env")

    load_dotenv(dotenv_path=dotenv_path)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    minio_client = MinioClient(
        minio_endpoint=os.getenv("MINIO_ENDPOINT"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY"),
        minio_bucket=os.getenv("MINIO_BUCKET"),
        minio_use_ssl=bool(int(os.getenv("MINIO_USE_SSL"))),
    )
    file_path = save_temp_file(minio_client.get_object("audio.mp3"))
    try:
        audio_info = get_audio_info(file_path)
        print("Audio Information:")
        print(f"Filename: {audio_info['filename']}")
        print(f"Length (seconds): {audio_info['length']}")
        print(f"Size (bytes): {audio_info['size']}")
        print(f"Bitrate: {audio_info['bitrate']} Hz")
        print(f"Sample Rate: {audio_info['samplerate']} Hz")
        print(f"Artist: {audio_info['artist']}")
        print(f"Genre: {audio_info['genre']}")
        print("Audio information saved to the PostgreSQL database.")
        # save_audio_info_to_db(audio_info)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.remove(file_path)
        logging.info(f"File {file_path} has been removed")
