from aiokafka import AIOKafkaConsumer
from os import environ
import json
import logging

logger = logging.getLogger(__name__)

async def consume_from_topic(*topics):
    while True:
        try:
            consumer = AIOKafkaConsumer(*topics, bootstrap_servers=environ['KAFKA_ADDRESS'], value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            await consumer.start()
            async for message in consumer:
                
                yield message.value, message.offset
        except Exception as e:
            logging.fatal(f"{e} - consume_from_topic")
            continue