from pydantic import BaseModel
from .metadata import Metadata

class Payload[T](BaseModel):
	data: T
	metadata: Metadata = None