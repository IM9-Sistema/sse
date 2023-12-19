from confluent_kafka import Consumer
from os import environ
import json
import logging

logger = logging.getLogger(__name__)

def consume_from_topic(*topics):
    while True:
        try:
            logger.info(f"Connecting to {environ['KAFKA_ADDRESS']}")
            consumer: Consumer = Consumer({
                'bootstrap.servers': environ['KAFKA_ADDRESS'],
                'group.id': 'sse',
            })
            logger.info(f"Subscribing to {', '.join(topics)}")
            consumer.subscribe(list(topics))
            logger.info(f"Subscribed to {", ".join(topics)}, polling...")
            while True:
                while data := consumer.poll():
                    yield json.loads(data.value()), data.offset()
        except Exception as e:
            logging.fatal(f"{e} - consume_from_topic")
            continue