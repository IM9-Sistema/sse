from fastapi import Query
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
import pyding
import json
from queue import Queue, Empty
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/positions')

@router.get('/')
async def get_positions(tracker: List[int] = Query(None)):
    def queue_positions():
        logger.info(tracker)
        if tracker:
            queue: Queue = pyding.queue('position.message', tracker_id=pyding.Contains(tracker))
        else:
            queue: Queue = pyding.queue('position.message')

        while True:
            try:
                data = queue.get(timeout=5)
                yield f"id: {data['id']}\nevent: position_update\ndata: {json.dumps({'type': 1, 'data': data['message']})}\n\n"
            except Empty:
                yield 'id: -1\nevent: keep-alive\ndata: {}\n\n'
    return StreamingResponse(queue_positions(), media_type="text/event-stream")