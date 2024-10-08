import json
from os import environ
from random import randint
from typing import List
from fastapi import APIRouter,Query
from fastapi.responses import StreamingResponse
from libs.auth import get_current_user
from libs.kafka_provider import consume_from_topic
from standards.structures import Event, Position, PrimitivePosition
from libs.database import trackers, users
from confluent_kafka import Consumer, OFFSET_END

router = APIRouter(prefix='/positions')

def handle(trackables_ids: list[int], user_id, offset=None):
	yield 'id: -1\nevent: connected\n\n'
	consumer = Consumer({"bootstrap.servers": "10.15.1.108:9092", "group.id":f"{randint(10000, 99999)}"})
	def assignment(consumer, partitions):
		for p in partitions:
			p.offset = offset or OFFSET_END
		consumer.assign(partitions)
	consumer.subscribe(["events__positions"], on_assign=assignment)
	while True:
		#print('poll')
		msg = consumer.poll()
		data = json.loads(msg.value())
		if not data: continue
		if not 'trackable' in data['data']: continue
		if trackables_ids and data['data']['trackable']['id'] not in trackables_ids: continue

		yield f"id: {msg.offset()}\nevent: message\nheaders: {{'content-type': 'application/json'}}\ndata: {json.dumps(data)}\n\n"


@router.get('/subscribe')
async def get_positions(token: str, trackableId: List[int] = Query(None), clientId: int = Query(None), offset: int = Query(None)) -> Event[Position]:

	current_user = int(get_current_user(token)) if token != environ.get("SSE_USER_BYPASS_TOKEN", -1) else 1304
	user_data = users.get_user(current_user)

	trackable_ids = []

	if trackableId:
		trackable_ids = [trackableId]

	elif clientId:
		trackable_ids = trackers.get_trackers(clientId, current_user)

	elif user_data['id_nivel_acesso'] < 1:
		trackable_ids = trackers.get_trackers(user_id=current_user)


	return StreamingResponse(handle(trackable_ids, current_user, offset), media_type="text/event-stream")