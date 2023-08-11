from aiokafka import AIOKafkaConsumer
from os import environ
import json

async def consume_from_topic(*topics):
    consumer = AIOKafkaConsumer(*topics, bootstrap_servers=environ['KAFKA_ADDRESS'], value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    await consumer.start()
    async for message in consumer:
        
        yield message.value, message.offset