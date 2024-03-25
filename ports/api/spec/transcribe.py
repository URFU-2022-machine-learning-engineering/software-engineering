from pydantic import BaseModel


class TranscribeResponse(BaseModel):
    detected_language: str
    recognized_text: str


class TranscribeRequest(BaseModel):
    bucket: str
    file_name: str
