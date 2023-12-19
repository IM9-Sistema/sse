from pydantic import BaseModel
from .metadata import Metadata

class Response[T](BaseModel):
	data: T
	metadata: Metadata = None