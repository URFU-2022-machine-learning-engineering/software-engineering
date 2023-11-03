# Transcription Service

This project is a transcription service built using FastAPI. It transcribes audio files using the WhisperTranscriber model.

## Installation

1. Clone the repository: git clone <https://github.com/URFU-2022-machine-learning-engineering/whisper-speech-recogniniton.git>
2. Navigate to the project directory: `cd whisper-speech-recogniniton`
3. Install Poetry (if not already installed): [Poetry Installation Guide](https://python-poetry.org/docs/)
4. Install the project dependencies using Poetry: poetry install

## Configuration

The service uses environment variables for configuration. Create a .env.local file in the project root directory and add the following variables:

```bash
MINIO_ENDPOINT=<MinIO endpoint URL>
MINIO_ACCESS_KEY=<MinIO access key>
MINIO_SECRET_KEY=<MinIO secret key>
```

Make sure to replace `MinIO endpoint URL`, `MinIO access key`, and `MinIO secret key` with your actual MinIO configuration.

## Usage

- Run the application: `poetry run uvicorn main:app`
- Open your browser and navigate to <http://localhost:8000> to check if the service is running. You should see a message saying "ready to transcribe."

## API Endpoints

### Transcribe

#### Endpoint: `/transcribe`

#### Method: `POST`

#### Request Body

```json
{
  "bucket": "audio-bucket",
  "file_name": "audio-file.mp3"
}
```

#### Response

```json
{
  "detected_language": "en",
  "recognized_text": "Transcribed text goes here"
}
```

#### Status Codes

- 200: Successful transcription
- 400: Bad request
- 500: Internal server error

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the GNU General Public License.
