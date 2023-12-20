from enum import StrEnum
from pydantic import BaseModel, Field
from .metadata import Metadata

class ResponseStatus(StrEnum):
	OK = 'Successful'
	NOT_FOUND = 'Not Found'
	UNPARSABLE = 'Fail during object parsing.'
	UNAVAILABLE = 'The service, method or endpoint you''re trying to query is not available right now.'
	QUEUED = 'Queued'
class Response[T](BaseModel):
	data: T|None
	detail: ResponseStatus = Field(default_factory=lambda: ResponseStatus.OK)
	metadata: Metadata|None = Field(default_factory=lambda: Metadata.now())

	@classmethod
	def from_status(cls, status: ResponseStatus, data: dict|None = None):
		return cls(data=data, detail=status)