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

from api.handlers import transcribe

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OTEL_EXPORTER_ENDPOINT = os.getenv("OTEL_EXPORTER_ENDPOINT")
if OTEL_EXPORTER_ENDPOINT == "":
    OTEL_EXPORTER_ENDPOINT = "localhost:4317"
    logger.warning("OTEL_EXPORTER_ENDPOINT is not set using localhost:4317")

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


@app.get("/")
def read_root():
    return {"message": "ready to transcribe"}
