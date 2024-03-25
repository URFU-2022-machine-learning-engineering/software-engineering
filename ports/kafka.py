import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from core import WhisperTranscriber
from ports.api.spec.transcribe import TranscribeRequest, TranscribeResponse

logger = logging.getLogger(__name__)


async def kafka_listener(consumer_topic: str, producer_topic: str, transcriber_config: dict, bootstrap_servers: str):
    consumer = AIOKafkaConsumer(consumer_topic, bootstrap_servers=bootstrap_servers, group_id="whisper-transcriber")
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    logger.info(f"Starting Kafka consumer for topic: {consumer_topic} and Kafka producer for topic: {producer_topic}")
    await consumer.start()
    await producer.start()
    logger.info("Kafka consumer and producer started successfully")
    try:
        async for msg in consumer:
            logger.debug(f"Received message: {msg.value.decode('utf-8')} from topic: {consumer_topic}")
            try:
                data = TranscribeRequest.parse_raw(msg.value)
            except Exception as e:
                logger.error(f"Error parsing message: {msg.value.decode('utf-8')} - {str(e)}")
                continue  # Skip to the next message

            logger.info(f"Processing file: {data.file_name} from bucket: {data.bucket}")
            try:
                whisper = WhisperTranscriber(**transcriber_config, minio_bucket=data.bucket)
                language, text = whisper.transcribe_audio(object_name=data.file_name)
                logger.info(f"Transcription completed for file: {data.file_name}. " f"Detected language: {language}. Detected text {text}")
            except Exception as e:
                logger.error(f"Error during transcription of file: {data.file_name} - {str(e)}")
                continue  # Skip to the next message

            response = TranscribeResponse(detected_language=language, recognized_text=text)
            result_msg = response.json().encode("utf-8")
            try:
                await producer.send_and_wait(topic=producer_topic, value=result_msg, key=data.file_name.encode("utf-8"))
                logger.info(f"Transcription result for file: {data.file_name} sent to topic: {producer_topic}")
            except Exception as e:
                logger.error(f"Error sending transcription result for file: {data.file_name} to topic: {producer_topic} - {str(e)}")

    finally:
        await consumer.stop()
        await producer.stop()
        logger.info("Kafka consumer and producer stopped")
