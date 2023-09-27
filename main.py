import logging

from fastapi import FastAPI

from api.handlers import transcribe

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", filename="/var/logs/whisper.log")
logging.getLogger(name=__name__)

app = FastAPI()

app.include_router(transcribe.router)


@app.get("/")
def read_root():
    return {"message": "ready to transcribe"}
