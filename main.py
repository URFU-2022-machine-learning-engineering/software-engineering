import logging

from fastapi import FastAPI

from api.handlers import transcribe

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

app.include_router(transcribe.router)


@app.get("/")
def read_root():
    return {"message": "ready to transcribe"}
