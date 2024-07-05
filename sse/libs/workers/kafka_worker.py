from queue import Queue
from libs.structures import Worker, CommandType, Command
from libs.database.alerts import get_alert_info, get_notation_info
from libs.kafka_provider import get_producer, produce
import pyding
import logging

logger = logging.getLogger('uvicorn')


class KafkaPublish(Worker):
	def work(self):
		queue: Queue = pyding.queue(
			'kafka.publish'
		)

		logger.info(f"Getting publisher")
		producer = get_producer()
		while True:
			data = queue.get()
			logger.debug(f"Producing kafka message {data["topic"]}@{data["message"]}")
			produce(producer, data['topic'], data['message'])
