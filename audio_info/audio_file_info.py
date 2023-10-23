import logging
import os

import eyed3
import librosa
from pydub import AudioSegment

import settings
from connectors import save_temp_file
from connectors.minio_connector import MinioClient
from connectors.postgres import save_audio_info_to_db


def get_audio_info(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        filename = os.path.basename(file_path)
        length = len(audio) / 1000  # Length in seconds
        size = os.path.getsize(file_path)  # Size in bytes
        bitrate = audio.frame_rate
        samplerate = audio.frame_rate

        # Extract MFCCs and Chroma features
        audio, sample_rate = librosa.load(file_path, sr=None)  # Load the audio file
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sample_rate)
        rmse = librosa.feature.rms(y=audio)
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)

        (
            artist,
            album,
            genre,
            year,
            lyrics,
            language,
            mood,
            instrumentation,
        ) = get_metadata(file_path)

        # Additional technical information
        audio_format, num_channels, audio_codec, bit_depth = get_technical_info(file_path)

        # Environmental or recording context
        location, recording_equipment, noise_level = get_environmental_info(file_path)

        return {
            "filename": filename,
            "length": length,
            "size": size,
            "bitrate": bitrate,
            "samplerate": samplerate,
            "mfccs": mfccs.tolist(),
            "chroma": chroma.tolist(),
            "spectral_centroid": spectral_centroid.tolist(),
            "zero_crossing_rate": zero_crossing_rate.tolist(),
            "spectral_bandwidth": spectral_bandwidth.tolist(),
            "spectral_contrast": spectral_contrast.tolist(),
            "rmse": rmse.tolist(),
            "tempo": tempo,
            "artist": artist,
            "album": album,
            "genre": genre,
            "year": year,
            "lyrics": lyrics,
            "language": language,
            "mood": mood,
            "instrumentation": instrumentation,
            "audio_format": audio_format,
            "num_channels": num_channels,
            "audio_codec": audio_codec,
            "bit_depth": bit_depth,
            "location": location,
            "recording_equipment": recording_equipment,
            "noise_level": noise_level,
        }
    except Exception as e:
        return {"error": str(e)}


def get_metadata(file_path):
    try:
        audiofile = eyed3.load(file_path)
        artist = audiofile.tag.artist
        album = audiofile.tag.album
        genre = audiofile.tag.genre.name if audiofile.tag.genre else None
        year = audiofile.tag.best_release_date
        lyrics = audiofile.tag.lyrics[0].text if audiofile.tag.lyrics else None
        language = audiofile.tag.language
        mood = None
        instrumentation = None
        return artist, album, genre, year, lyrics, language, mood, instrumentation
    except Exception as e:
        logging.error(f"Error during get metadata {e}")
        return None, None, None, None, None, None, None, None


# Example functions to extract technical information from the audio file (replace with your actual methods)
def get_technical_info(file_path):
    try:
        audiofile = eyed3.load(file_path)
        audio_format = audiofile.info.format
        num_channels = audiofile.info.mode
        audio_codec = audiofile.info.audio_format
        bit_depth = audiofile.info.bits_per_sample
        return audio_format, num_channels, audio_codec, bit_depth
    except Exception as e:
        logging.error(f"Error during get technical info {e}")
        return None, None, None, None


def get_environmental_info(file_path):
    location = None
    recording_equipment = None
    noise_level = None
    return location, recording_equipment, noise_level


if __name__ == "__main__":
    minio_client = MinioClient(
        minio_endpoint=settings.MINIO_ENDPOINT,
        minio_access_key=settings.MINIO_ACCESS_KEY,
        minio_secret_key=settings.MINIO_SECRET_KEY,
        minio_bucket=settings.MINIO_BUCKET,
        minio_use_ssl=settings.MINIO_USE_SSL,
    )

    file_path = save_temp_file(minio_client.get_object("audio.mp3"))
    audio_info = get_audio_info(file_path)

    if "error" in audio_info:
        print(f"Error: {audio_info['error']}")
    # TODO: Change prints to logging
    else:
        print("Audio Information:")
        print(f"Filename: {audio_info['filename']}")
        print(f"Length (seconds): {audio_info['length']}")
        print(f"Size (bytes): {audio_info['size']}")
        print(f"Bitrate: {audio_info['bitrate']} Hz")
        print(f"Sample Rate: {audio_info['samplerate']} Hz")
        # print(f"MFCCs: {audio_info['mfccs']}")
        # print(f"Chroma Features: {audio_info['chroma']}")
        # print(f"Spectral Centroid: {audio_info['spectral_centroid']}")
        # print(f"Zero-Crossing Rate: {audio_info['zero_crossing_rate']}")
        # print(f"Spectral Bandwidth: {audio_info['spectral_bandwidth']}")
        # print(f"Spectral Contrast: {audio_info['spectral_contrast']}")
        # print(f"Root Mean Square Energy (RMSE): {audio_info['rmse']}")
        print(f"Tempo: {audio_info['tempo']}")
        print(f"Artist: {audio_info['artist']}")
        print(f"Album: {audio_info['album']}")
        print(f"Genre: {audio_info['genre']}")
        print(f"Year: {audio_info['year']}")
        print(f"Lyrics: {audio_info['lyrics']}")
        print(f"Language: {audio_info['language']}")
        print(f"Mood: {audio_info['mood']}")
        print(f"Instrumentation: {audio_info['instrumentation']}")
        print(f"Audio Format: {audio_info['audio_format']}")
        print(f"Number of Channels: {audio_info['num_channels']}")
        print(f"Audio Codec: {audio_info['audio_codec']}")
        print(f"Bit Depth: {audio_info['bit_depth']}")
        print(f"Location: {audio_info['location']}")
        print(f"Recording Equipment: {audio_info['recording_equipment']}")
        print(f"Noise Level: {audio_info['noise_level']}")

        save_audio_info_to_db(audio_info)
        print("Audio information saved to the PostgreSQL database.")
