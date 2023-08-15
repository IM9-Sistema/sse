from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt 
from .utils import get_secret_key
from .structures import TokenData


ALGORITHM = 'HS256'
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
