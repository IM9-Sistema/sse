import json
from os import environ
from typing import List
from fastapi import APIRouter,Query
from fastapi.responses import StreamingResponse
from libs.auth import get_current_user
from libs.kafka_provider import consume_from_topic
from standards.structures import Event, Position, PrimitivePosition
from libs.database import trackers, users

router = APIRouter(prefix='/positions')

def handle(trackables_ids: list[int]):
	yield 'id: -1\nevent: connected'
	for data, id in consume_from_topic('events__positions'):
		if not 'trackable' in data['data']: continue
		if trackables_ids and data['data']['trackable']['id'] not in trackables_ids: continue
		yield f"id: {id}\nevent: message\nheaders: {{'content-type': 'application/json'}}\ndata: {json.dumps(data)}\n\n"


@router.get('/subscribe')
async def get_positions(token: str, trackableId: List[int] = Query(None), clientId: int = Query(None	)) -> Event[Position]:

	current_user = int(get_current_user(token)) if token != environ.get("SSE_USER_BYPASS_TOKEN", -1) else 1304
	user_data = users.get_user(current_user)

	trackable_ids = []

	if trackableId:
		trackable_ids = [trackableId]

	elif clientId:
		trackable_ids = trackers.get_trackers(clientId, current_user)

	elif user_data['id_nivel_acesso'] < 1:
		trackable_ids = trackers.get_trackers(user_id=current_user)


	return StreamingResponse(handle(trackable_ids), media_type="text/event-stream")