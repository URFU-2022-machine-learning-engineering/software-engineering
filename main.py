from fastapi import FastAPI

from api.handlers import transcribe

app = FastAPI()

app.include_router(transcribe.router)


@app.get("/")
def read_root():
    return {"message": "ready to transcribe"}
