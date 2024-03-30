import logging
import os

logger = logging.getLogger(__name__)

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
