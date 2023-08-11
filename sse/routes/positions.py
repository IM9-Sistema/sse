from fastapi import Query
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
import pyding
from pyding.structures import QueuedHandler
import json
from queue import Queue, Empty
from typing import List
import logging
import fastapi

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/positions')

@router.get('/')
async def get_positions(background_tasks: fastapi.background.BackgroundTasks, tracker: List[int] = Query(None)):
    # Setup handler
    if tracker:
        handler: QueuedHandler = pyding.queue('position.message', tracker_id=pyding.Contains(tracker))
    else:
        handler: QueuedHandler = pyding.queue('position.message', tracker_id=pyding.Contains(tracker))
    queue: Queue = handler.get_queue()
    background_tasks.add_task(lambda h: h.unregister(), handler)
    
    def queue_positions(queue):
        while True:
            try:
                data = queue.get(timeout=5)
                yield f"id: {data['id']}\nevent: position_update\ndata: {json.dumps({'type': 1, 'data': data['message']})}\n\n"
            except Empty:
                yield 'id: -1\nevent: keep-alive\ndata: {}\n\n'

    return StreamingResponse(queue_positions(queue), media_type="text/event-stream")