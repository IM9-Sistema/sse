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
