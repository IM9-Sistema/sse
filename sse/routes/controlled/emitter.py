import json
import logging
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from libs.auth import create_sse_session, get_sse_session
import pyding
from libs.structures import Session, Response, Command, Payload, ResponseStatus

logger = logging.getLogger("uvicorn")

router = APIRouter(prefix='/emitter', tags=['controlled', 'event emission'])

@router.websocket('/')
async def event_emitter(websocket: WebSocket, session: Session = Depends(get_sse_session)) -> Response[None]:
	await websocket.accept()
	try:
		while data := await websocket.receive_json():
			try:
				command = Command(**(data|{'origin': session}))
				logger.info(f'Recieved from {session.session.origin} @ {session.session.name}')
				pyding.call('commands.recieve', command=command, command_id=command.command_id)
				response = Response.from_status(ResponseStatus.QUEUED, data=command)
			except ValidationError as e:
				logger.critical(f'Failed to parse: {data!r} from {session.session.origin} @ {session.session.name}')
				response = Response.from_status(ResponseStatus.UNPARSABLE, data=e.errors())
			
			await websocket.send_json(json.loads(response.model_dump_json()))
	except WebSocketDisconnect:
		return


@router.post('/', status_code=202)
async def event_emitter(command: Payload[Command], session: Session = Depends(get_sse_session)) -> Response[Command]:
	command = command.data
	command.origin = session
	pyding.call('commands.recieve', command=command, command_id=command.command_id)
	return Response.from_status(ResponseStatus.QUEUED, data=command)