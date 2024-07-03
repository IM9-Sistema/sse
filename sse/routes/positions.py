from os import environ
import queue
from time import time
from fastapi import Depends, Query, status
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
import pyding
from pyding.structures import QueuedHandler
from libs.auth import get_current_user
import json
from libs.structures import TokenData
from libs.database import trackers, users
from queue import Queue, Empty
from typing import Annotated, List
import logging
import fastapi

logger = logging.getLogger('uvicorn')

router = APIRouter(prefix='/positions')

def queue_positions(queue: queue.Queue, is_debug: bool = None):
	warn_timeout = 5
	last_warning = time()
	if is_debug:
		logger.info("Sent connected")
	yield 'id: -1\nevent: connected\ndata: {}\n\n'
	while True:
		try:
			if is_debug:
				logger.info("Sent data")
			data = queue.get(timeout=5)
			if (size := queue.qsize()) > 50 and (time() - last_warning) >= warn_timeout:
				yield f"id: {data['id']}\nevent: warning\ndata: {json.dumps({'message': f'You are lagging behind. This connection\'s queue length is greater than 50 (currently {size}).', 'error': False})}\n\n"
				last_warning = time()

			yield f"id: {data['id']}\nevent: position_update\ndata: {json.dumps({'type': 1, 'data': data['message']})}\n\n"
		except Empty:
			yield 'id: -1\nevent: keep-alive\ndata: {}\n\n'

@router.get('/subscribe',
			responses={
				200: {
					'content': {
						'text/event-stream': "id: int\nevent: position_update\ndata: {}\n\n"
					},
					'description': 'Returns a event-stream whenever a tracker updates its position'
				}
			}
		)
@router.get('/',
			responses={
				200: {
					'content': {
						'text/event-stream': "id: int\nevent: position_update\ndata: {}\n\n"
					},
					'description': 'Depricated. use /subscribe'
				}
			}
		)
async def get_positions(background_tasks: fastapi.background.BackgroundTasks, \
						token: str, \
						tracker: List[int] = Query(None),
						clientId: int = Query(None),
						debug: bool = Query(None)):
	# Setup handler

		
	current_user = int(get_current_user(token)) if token != environ.get("SSE_USER_BYPASS_TOKEN", -1) else 1304
	user_data = users.get_user(current_user)

	args = {}

	if tracker:
		args['tracker_id'] = pyding.Contains(tracker)

	elif clientId:
		args['tracker_id'] = pyding.Contains(trackers.get_trackers(clientId, current_user))

	elif user_data['id_nivel_acesso'] < 1:
		args['tracker_id'] = pyding.Contains(trackers.get_trackers(user_id=current_user))

	handler: QueuedHandler = pyding.queue('position.message', **args, return_handler=True)
	queue: Queue = handler.get_queue()

	def unregister(handler: QueuedHandler):
		logger.info(f"Closing handler ({handler})")
		handler.unregister()
	
	background_tasks.add_task(unregister, handler)

	return StreamingResponse(queue_positions(queue, debug), media_type="text/event-stream")