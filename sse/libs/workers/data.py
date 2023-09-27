from libs.structures import Worker
from libs.consumer import consume_from_topic
import pyding
import logging

logger = logging.getLogger(__name__)


class PositionWorker(Worker):
    async def work(self):
        while True:
            async for message, id in consume_from_topic('positions'):
                try:
                    pyding.call('position.message', message=message, id=id, tracker_id=message['rastreador']['id'], **message)
                except KeyError:
                    logger.critical("Failed to get data from kafka.")
                    logger.critical(f"{message}")
    @classmethod
    def begin(cls):
        instance = cls()
        instance.start()
        return instance


class AlertWorker(Worker):
    async def work(self):
        while True:
            async for message, id in consume_from_topic('alerts'):
                pyding.call('alert.message', **message)

    @classmethod
    def begin(cls):
        instance = cls()
        instance.start()
        return instance
