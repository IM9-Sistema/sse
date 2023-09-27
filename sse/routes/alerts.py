from fastapi import Depends, Query
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/alerts')

def queue_positions(queue):
    yield 'id: -1\nevent: connected\ndata: {}\n\n'
    while True:
        try:
            data = queue.get(timeout=5)
            yield f"id: {data['id']}\nevent: position_update\ndata: {json.dumps({'type': 1, 'data': data['message']})}\n\n"
        except Empty:
            yield 'id: -1\nevent: keep-alive\ndata: {}\n\n'

@router.get('/',
            responses={
                200: {
                    'content': {
                        'text/event-stream': "id: int\nevent: position_update\ndata: {}\n\n"
                    },
                    'description': 'Returns a event-stream whenever a tracker updates its position'
                }
            }
        )
async def get_positions(background_tasks: fastapi.background.BackgroundTasks, \
                        tracker: List[int] = Query(None),
                        clientId: int = Query(None),
                        sleep: int = Query(0, description='Sleep time between ')):
    # Setup handler
    current_user = 1304
    user_data = users.get_user(current_user)

    args = {}

    handler: QueuedHandler = pyding.queue('alert.message', **args, return_handler=True)
    queue: Queue = handler.get_queue()

    def unregister(handler: QueuedHandler):
        logger.info(f"Closing handler ({handler})")
        handler.unregister()
    
    background_tasks.add_task(unregister, handler)

    return StreamingResponse(queue_positions(queue), media_type="text/event-stream")