import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from fastapi import FastAPI

from api.handlers import transcribe

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger(name=__name__)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("whisper.speech.recognition")

app = FastAPI()

app.include_router(transcribe.router)


@tracer.start_as_current_span("/")
@app.get("/")
def read_root():
    return {"message": "ready to transcribe"}
