from os import environ
from base64 import b64decode


def get_secret_key() -> bytes:
    return b64decode(environ.get('JWT_KEY'))