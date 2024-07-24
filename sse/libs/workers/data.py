import asyncio
from queue import Queue
from libs.structures import Worker, CommandType, Command
from libs.database.alerts import get_alert_info, get_notation_info
from libs.database.equip import get_equip_serial
from libs.database import RedisCache, equip_pool
from libs.kafka_provider import consume_from_topic
import pyding
import logging

logger = logging.getLogger('uvicorn')


class PositionGather(Worker):
    def work(self):
        cache = RedisCache(equip_pool)
        
        while True:
            for message, id in consume_from_topic('positions'):
                match message:
                    case {"rastreador": {"equipamento": {"id": id, **_eq}, **_rastr}, **payload}:
                        message['rastreador']['equipamento']['serial'] = int(asyncio.run(cache.get(id)))
                        
                try:
                    pyding.call('position.message', message=message, id=int(id), tracker_id=int(message['rastreador']['id']), **message)
                except KeyError:
                    logger.critical("Failed to get data from kafka.")
                    logger.critical(f"{message}")




class ProcessAlerts(Worker):
    def work(self):
        queue: Queue = pyding.queue(
            'commands.recieve',
            command_id=pyding.Contains([
                    CommandType.ALERT_CREATE,
                    CommandType.ALERT_DELETE,
                    CommandType.ALERT_UPDATE
            ])
        )

        while True:
            event = queue.get()
            command: Command = event['command']
            alert_data = get_alert_info(command.data['id'])
            if alert_data:
                pyding.call('kafka.publish', topic='alerts', message={"origin": "SSE", "event": command.command_id, "data": alert_data})

class ProcessNotations(Worker):
    def work(self):
        queue: Queue = pyding.queue(
            'commands.recieve',
            command_id=pyding.Contains([
                    CommandType.NOTATION_CREATE,
                    CommandType.NOTATION_DELETE,
                    CommandType.NOTATION_UPDATE
            ])
        )

        while True:
            event = queue.get()
            command: Command = event['command']
            notation_data = get_notation_info(command.data['id'])
            if notation_data:
                pyding.call('kafka.publish', topic='alerts', message={"origin": "SSE", "event": command.command_id, "data": notation_data})


class EquipamentsGather(Worker):
    def work(self):
        while True:
            cache = RedisCache(equip_pool)
            data = get_equip_serial()
            for equip in data:
                cache.set(equip['key'], equip['value'])

class AlertsGather(Worker):
    def work(self):
        while True:
            for message, id in consume_from_topic('alerts', 'anchors'):
                try:
                    pyding.call('alerts.message', id=id, message=message)
                except KeyError:
                    logger.critical("Failed to get data from kafka.")
                    logger.critical(f"{message}")


    