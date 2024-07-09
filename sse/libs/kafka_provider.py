from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from os import environ
import json
import logging

logger = logging.getLogger('uvicorn')

def get_producer() -> KafkaProducer:
    return KafkaProducer(bootstrap_servers=environ['KAFKA_ADDRESS'])

def produce(producer: KafkaProducer, topic: str, message: str):
    producer.send(topic, json.dumps(message, default=lambda x: int(x.timestamp()) if isinstance(x, datetime) else str(x)).encode('utf-8'))
    producer.flush()

def fix_ints(object: dict):
    for key, value in object.items():
        if isinstance(value, str) and value.isnumeric():
            object[key] = int(value)
        elif isinstance(value, dict):
            fix_ints(value)
    return object


def consume_from_topic(*topics):
    while True:
        try:
            logger.debug(f"Connecting to {environ['KAFKA_ADDRESS']}")
            consumer: KafkaConsumer = KafkaConsumer(*topics, bootstrap_servers=environ['KAFKA_ADDRESS'], value_deserializer=lambda x: fix_ints(json.loads(x.decode('utf-8'))))
            logger.debug(f"Subscribed to {", ".join(topics)}, polling...")
            for msg in consumer:
                yield msg.value, msg.offset
        except Exception as e:
            logging.fatal(f"{e} - consume_from_topic")
            continue