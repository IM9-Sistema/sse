from os import environ
from base64 import b64decode
from random import choices
from string import ascii_letters


def get_secret_key() -> bytes:
    return b64decode(environ.get('JWT_KEY'))

def get_sse_key() -> str:
    return environ.get('SSE_SESSION_KEY')

def random_string(length: int = None):
	return "".join(choices(ascii_letters, k=length or 32))
