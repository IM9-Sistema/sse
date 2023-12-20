from libs.structures import Worker
from libs.consumer import consume_from_topic
import pyding
import logging

logger = logging.getLogger('uvicorn')


class PositionGather(Worker):
    def work(self):
        while True:
            for message, id in consume_from_topic('positions'):
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


class AlertsGather(Worker):
    def work(self):
        while True:
            for message, id in consume_from_topic('contacts', 'database.eventos.EVENTOS.dbo.TB_SISTEMA_TRATATIVAS', 'database.eventos.EVENTOS.dbo.TB_SISTEMA', 'anchors'):
                try:
                    pyding.call('alerts.message', id=id, message=message)
                except KeyError:
                    logger.critical("Failed to get data from kafka.")
                    logger.critical(f"{message}")

    @classmethod
    def begin(cls):
        instance = cls()
        instance.start()
        return instance
    