from typing import Annotated
from uuid import uuid4
from fastapi import Body, Depends, HTTPException, Header, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt 
from .utils import get_secret_key, get_sse_key, random_string
from .structures import TokenData, Payload, SessionIdentifier, Session
from .database import RedisCache

ALGORITHM = 'HS256'
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")
sessions = {}

def get_current_user(token: Annotated[str, Depends(oauth_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not verify your authentication details.',
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )

    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return int(username)

    except JWTError as e:
        raise credentials_exception

async def get_sse_session(x_sse_session: Annotated[str, Header()]) -> Session:
    cache = RedisCache()
    session = await cache.get(x_sse_session, Session)
    if not session:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect sse session."
        )
    return session

async def create_sse_session(request: Request, session_identification: Annotated[Payload[SessionIdentifier], Body()], x_sse_key: Annotated[str, Header()]) -> Session:
    if x_sse_key != get_sse_key():
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect sse key."
        )

    redis = RedisCache()

    session_id = session_identification.data
    session = Session(
        session=session_id,
        id=uuid4(),
        token=random_string(128)
    )
    await redis.set(session.token, session)
    return session


