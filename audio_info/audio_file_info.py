import logging
import os

import eyed3
import librosa
from pydub import AudioSegment

import settings
from connectors import save_temp_file
from connectors.minio_connector import MinioClient
from connectors.postgres import save_audio_info_to_db


class AudioInfo:
    def __init__(self, file_path: str):
        self.audio_file_path = file_path
        self.audio_file = AudioSegment.from_file(self.audio_file_path)
        self.audio_file_name = os.path.basename(self.audio_file_path)
        self.audio_file_size = os.path.getsize(self.audio_file_path)
        self.audio_file_length = len(self.audio_file) / 1000  # Length in seconds
        self.bitrate = (8 * self.audio_file_size) / self.audio_file_length
        self.sample_rate = self.audio_file.frame_rate

    def get_basic_audio_info(self) -> dict:
        return {
            "filename": self.audio_file_name,
            "length": self.audio_file_length,
            "size": self.audio_file_size,
            "bitrate": self.bitrate,
            "samplerate": self.sample_rate,
        }

    def get_id3_tags(self) -> dict:
        id3_tags = {
            "artist": None,
            "album": None,
            "genre": None,
            "year": None,
            "lyrics": None,
            "language": None,
        }
        try:
            audiofile = eyed3.load(self.file_path)
            id3_tags["artist"] = audiofile.tag.artist if audiofile.tag.artist else None
            id3_tags["album"] = audiofile.tag.album if audiofile.tag.album else None
            id3_tags["genre"] = audiofile.tag.genre.name if audiofile.tag.genre else None
            id3_tags["year"] = audiofile.tag.best_release_date if audiofile.tag.best_release_date else None
            id3_tags["lyrics"] = audiofile.tag.lyrics[0].text if audiofile.tag.lyrics else None
            id3_tags["language"] = audiofile.tag.language if audiofile.tag.language else None
            return id3_tags
        except Exception as e:
            logging.error(f"Error during get id3_tags {e}")
            return id3_tags

    def get_audio_features(self) -> dict:
        audio_features = {
            "mfccs": None,
            "chroma": None,
            "spectral_centroid": None,
            "zero_crossing_rate": None,
            "spectral_bandwidth": None,
            "spectral_contrast": None,
            "rmse": None,
            "tempo": None,
            "beats": None,
        }
        try:
            # Extract MFCCs and Chroma features
            audio, sample_rate = librosa.load(self.audio_file_path, sr=None)  # Load the audio file
            audio_features["mfccs"] = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
            audio_features["chroma"] = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            audio_features["spectral_centroid"] = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
            audio_features["zero_crossing_rate"] = librosa.feature.zero_crossing_rate(audio)[0]
            audio_features["spectral_bandwidth"] = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)
            audio_features["spectral_contrast"] = librosa.feature.spectral_contrast(y=audio, sr=sample_rate)
            audio_features["rmse"] = librosa.feature.rms(y=audio)
            audio_features["tempo"], audio_features["beats"] = librosa.beat.beat_track(y=audio, sr=sample_rate)
            return audio_features
        except Exception as e:
            logging.error(f"Error during get audio features {e}")
            return audio_features


if __name__ == "__main__":
    from random import choice

    minio_client = MinioClient(
        minio_endpoint=settings.MINIO_ENDPOINT,
        minio_access_key=settings.MINIO_ACCESS_KEY,
        minio_secret_key=settings.MINIO_SECRET_KEY,
        minio_bucket=settings.MINIO_BUCKET,
        minio_use_ssl=settings.MINIO_USE_SSL,
    )
    objects_list = [o.object_name for o in minio_client.get_list_of_objects()]
    FILENAME = choice(objects_list)
    FILEPATH = save_temp_file(minio_client.get_object(FILENAME), prefix=FILENAME)

    audio_info = AudioInfo(file_path=FILEPATH)

    basic_audio_info = audio_info.get_basic_audio_info()
    id3_tags = audio_info.get_id3_tags()
    audio_features = audio_info.get_audio_features()

    # TODO: Save audio information to the database in a separate functions
    save_audio_info_to_db(basic_audio_info, id3_tags, audio_features)
    logging.info("Audio information saved to the database.")
