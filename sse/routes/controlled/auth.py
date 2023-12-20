from fastapi import APIRouter,Depends
from libs.auth import create_sse_session, get_sse_session
from libs.structures import Session, Response

router = APIRouter(prefix='/auth', tags=['controlled', 'authentication'])

@router.post('/')
async def authenticate(session: Session = Depends(create_sse_session)) -> Response[Session]:
	return Response(data=session)

@router.get('/')
async def authenticate(session: Session = Depends(get_sse_session)) -> Response[Session]:
	return Response(data=session)

