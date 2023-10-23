from fastapi import Depends, HTTPException, Query, status
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

def queue_alerts(queue):
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
                        'text/event-stream': "id: int\nevent: eventname\ndata: {}\n\n"
                    },
                    'description': 'Returns a event-stream whenever an alerts changes'
                }
            }
        )
async def get_alerts(background_tasks: fastapi.background.BackgroundTasks, \
                        token: str):
    # Setup handler
    current_user = int(get_current_user(token))
    user_data = users.get_user(current_user)

    args = {}

    if user_data['id_nivel_acesso'] < 1:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not verify your authentication details.',
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )

    handler: QueuedHandler = pyding.queue('alerts.message', **args, return_handler=True)
    queue: Queue = handler.get_queue()

    def unregister(handler: QueuedHandler):
        logger.info(f"Closing handler ({handler})")
        handler.unregister()
    
    background_tasks.add_task(unregister, handler)

    return StreamingResponse(queue_alerts(queue), media_type="text/event-stream")