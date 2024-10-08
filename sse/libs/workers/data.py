import asyncio
from queue import Queue
from time import sleep

import dateutil
import dateutil.parser
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
		equip_data = {int(i['key']): str(i['value']) for i in get_equip_serial()}
		
		while True:
			for message, id in consume_from_topic('positions'):
				match message:
					case {"rastreador": {"equipamento": {"id": equip_id, **_eq}, **_rastr}, **payload}:
						if int(equip_id) in equip_data:
							message['rastreador']['equipamento']['serial'] = equip_data[int(equip_id)]
				try:
					message['position']['time']['recieved_at'] = dateutil.parser.parse(message['position']['time']['recieved_at']).strftime('%Y-%m-%dT%H:%M:%S')
				except:
					logger.critical(f'Failed to adjust timestamp for {message}')
				
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


class AlertsGather(Worker):
	def work(self):
		while True:
			for message, id in consume_from_topic('alerts', 'anchors'):
				try:
					pyding.call('alerts.message', id=id, message=message)
				except KeyError:
					logger.critical("Failed to get data from kafka.")
					logger.critical(f"{message}")

