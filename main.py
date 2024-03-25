import asyncio
import logging
import os

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core import (
    minio_access_key,
    minio_endpoint,
    minio_secret_key,
    minio_use_ssl,
    model_name,
)
from ports.api.handlers import transcribe
from ports.kafka import kafka_listener

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", style="{")
logger = logging.getLogger(__name__)

logging.getLogger("aiokafka").setLevel(logging.INFO)

# TODO: Move to setup
OTEL_EXPORTER_ENDPOINT = os.getenv("OTEL_EXPORTER_ENDPOINT")

# kafka topics
PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC")
CONSUMER_TOPIC = os.getenv("CONSUMER_TOPIC")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

if KAFKA_BOOTSTRAP_SERVERS == "":
    KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
    logger.warning("KAFKA_BOOTSTRAP_SERVERS is not set using localhost:9092")

if OTEL_EXPORTER_ENDPOINT == "":
    OTEL_EXPORTER_ENDPOINT = "localhost:4317"
    logger.warning("OTEL_EXPORTER_ENDPOINT is not set using localhost:4317")

if PRODUCER_TOPIC == "":
    PRODUCER_TOPIC = "recognition"
    logger.warning("PRODUCER_TOPIC is not set using recognition")

if CONSUMER_TOPIC == "":
    CONSUMER_TOPIC = "send-data"
    logger.warning("CONSUMER_TOPIC is not set using send-data")

# TODO: Move to ports
# Define a common resource for both Tracer and Meter providers
resource = Resource(attributes={"service.name": "Whisper Speech Recognition Service"})

# Setup Tracer Provider and Processor
trace_provider = TracerProvider(resource=resource)
trace_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True))
trace_provider.add_span_processor(trace_processor)
trace.set_tracer_provider(trace_provider)

# Setup Meter Provider
meter_provider = MeterProvider(
    resource=resource, metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True))]
)
metrics.set_meter_provider(meter_provider)

app = FastAPI()

app.include_router(transcribe.router)

FastAPIInstrumentor.instrument_app(app, tracer_provider=trace_provider)

logger.debug(f"Model name: {model_name}")
logger.debug(f"Minio endpoint: {minio_endpoint}")
logger.debug(f"Kafka bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
logger.debug(f"Producer topic: {PRODUCER_TOPIC}")
logger.debug(f"Consumer topic: {CONSUMER_TOPIC}")


@app.on_event("startup")
async def startup_event():
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


@app.on_event("shutdown")
async def shutdown_event():
    # Cancel the Kafka listener task on application shutdown
    app.state.kafka_listener_task.cancel()
    try:
        # Wait for the task cancellation to complete, with a timeout to prevent hanging
        await asyncio.wait_for(app.state.kafka_listener_task, timeout=10)
    except asyncio.TimeoutError:
        logger.error("Kafka listener task cancellation timed out.")


@app.get("/")
async def read_root():
    return {"message": "ready to transcribe"}
