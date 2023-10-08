from enum import StrEnum

from pydantic import BaseModel


class WhisperModels(StrEnum):
    tiny_en = "tiny.en"
    tiny = "tiny"
    base_en = "base.en"
    base = "base"
    small_en = "small.en"
    small = "small"
    medium_en = "medium.en"
    medium = "medium"
    large_v1 = "large-v1"
    large_v2 = "large-v2"
    large = "large-v2"


class TranscribeResponse(BaseModel):
    detected_language: str
    recognized_text: str


class TranscribeRequest(BaseModel):
    model: WhisperModels | None
    bucket: str
    file_name: str
