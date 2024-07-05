from fastapi import APIRouter,Depends
from fastapi.responses import StreamingResponse
from libs.auth import create_sse_session, get_sse_session
from libs.structures import Session, Response
from libs.kafka_provider import consume_from_topic

router = APIRouter(prefix='/subscribe', tags=['controlled', 'events'])

def handle(topic: str):
	for data, id in consume_from_topic(topic):
		yield f"id: {id}\nevent: message\ntopic: {topic}\ndata: {data}"

@router.get('/subscribe/{topic}')
async def authenticate(topic: str, session: Session = Depends(get_sse_session)) -> Response[Session]:
	return StreamingResponse(handle(), media_type="text/event-stream")
    
