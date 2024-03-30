from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from settings import OTEL_EXPORTER_ENDPOINT

RESOURCE = Resource(attributes={"service.name": "Whisper Speech Recognition Service"})


def init_tracing() -> TracerProvider:
    # Setup Tracer Provider and Processor
    trace_provider = TracerProvider(resource=RESOURCE)
    trace_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True))
    trace_provider.add_span_processor(trace_processor)
    trace.set_tracer_provider(trace_provider)
    return trace_provider


def init_metrics() -> MeterProvider:
    # Setup Meter Provider
    meter_provider = MeterProvider(
        resource=RESOURCE, metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True))]
    )
    metrics.set_meter_provider(meter_provider)
    return meter_provider
