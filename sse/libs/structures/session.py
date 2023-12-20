from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class SessionIdentifier(BaseModel):
	name: str
	project: str
	origin: str

class Session(BaseModel):
	session: SessionIdentifier
	id: UUID
	token: str
	created_on: datetime = Field(default_factory=lambda: datetime.utcnow())
