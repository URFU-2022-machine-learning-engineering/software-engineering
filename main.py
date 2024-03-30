import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from core import (
    minio_access_key,
    minio_endpoint,
    minio_secret_key,
    minio_use_ssl,
    model_name,
)
from ports.api.handlers import transcribe
from ports.kafka import kafka_listener
from ports.otel.otel import init_metrics, init_tracing
from settings import CONSUMER_TOPIC, KAFKA_BOOTSTRAP_SERVERS, PRODUCER_TOPIC

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", style="{")
logger = logging.getLogger(__name__)

logging.getLogger("aiokafka").setLevel(logging.INFO)


def init_fastapi_instrumentation():
    tracer_provider = init_tracing()
    meter_provider = init_metrics()
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider, meter_provider=meter_provider)


logger.debug(f"Model name: {model_name}")
logger.debug(f"Minio endpoint: {minio_endpoint}")
logger.debug(f"Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
logger.debug(f"Producer topic: {PRODUCER_TOPIC}")
logger.debug(f"Consumer topic: {CONSUMER_TOPIC}")


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    transcriber_config = {
        "model_name": model_name,
        "minio_endpoint": minio_endpoint,
        "minio_access_key": minio_access_key,
        "minio_secret_key": minio_secret_key,
        "minio_use_ssl": minio_use_ssl,
    }
    # Start Kafka listener as a background task and store the reference in the app state
    app.state.kafka_listener_task = asyncio.create_task(
        kafka_listener(
            consumer_topic=CONSUMER_TOPIC, producer_topic=PRODUCER_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, transcriber_config=transcriber_config
        )
    )
    yield
    # Cancel the Kafka listener task on application shutdown
    app.state.kafka_listener_task.cancel()
    try:
        # Wait for the task cancellation to complete, with a timeout to prevent hanging
        await asyncio.wait_for(app.state.kafka_listener_task, timeout=10)
    except asyncio.TimeoutError:
        logger.error("Kafka listener task cancellation timed out.")


app = FastAPI(lifespan=app_lifespan)

app.include_router(transcribe.router)


@app.get("/")
async def read_root():
    return {"message": "ready to transcribe"}
