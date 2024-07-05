from os import environ
from base64 import b64decode
from random import choices
from string import ascii_letters


def get_secret_key() -> bytes:
    return b64decode(environ.get('JWT_KEY'))

def get_sse_key() -> str:
    return environ.get('X_SSE_KEY')

def random_string(length: int = None):
	return "".join(choices(ascii_letters, k=length or 32))

def get_pepper() -> bytes:
    return b64decode(environ.get('SECRET_PEPPER')).decode("utf-8")
