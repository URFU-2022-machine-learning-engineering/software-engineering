import whisper
from minio import Minio
import io


class WhisperTranscriber:
    def __init__(self, model_name, minio_endpoint, minio_access_key, minio_secret_key, minio_bucket):
        self.model = whisper.load_model(model_name)
        self.minio_client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
        )
        self.bucket = minio_bucket

    def transcribe_audio(self, object_name):
        # get log-Mel spectrogram from Minio
        mel = self._get_log_mel_spectrogram(object_name)
        # detect the spoken language
        _, probs = self.model.detect_language(mel)
        language = max(probs, key=probs.get)
        # decode the audio
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(self.model, mel, options)
        return language, result.text

    def _get_log_mel_spectrogram(self, object_name):
        # get object from Minio
        object_data = self.minio_client.get_object(self.bucket, object_name)
        # read object data into memory
        object_bytes = io.BytesIO(object_data.read())
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(object_bytes)
        audio = whisper.pad_or_trim(audio)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        return mel


if __name__ == "__main__":
    transcriber = WhisperTranscriber(
        model_name="large",
        minio_endpoint="your-minio-endpoint",
        minio_access_key="your-access-key",
        minio_secret_key="your-secret-key",
        minio_bucket="your-bucket-name",
    )

    language, text = transcriber.transcribe_audio("your-audio-object-name")
    print(f"Detected language: {language}")
    print(f"Recognized text: {text}")
