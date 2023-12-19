from datetime import datetime
from pydantic import BaseModel


class Metadata[T](BaseModel):
	data: T
	created_by: str
	created_on: datetime
	details: str