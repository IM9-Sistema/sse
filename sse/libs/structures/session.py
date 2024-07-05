from datetime import datetime
from libs.utils import tokens
from uuid import UUID
from pydantic import BaseModel, Field
import hashlib


class SessionIdentifier(BaseModel):
	name: str
	project: str
	origin: str

class Session(BaseModel):
	session: SessionIdentifier
	id: UUID
	token: str
	created_on: datetime = Field(default_factory=lambda: datetime.utcnow())

	@staticmethod
	def get_hash(token: str) -> str:
		mixed = "".join([a+b for a,b in zip(tokens.get_pepper(), token)])

		hashed = hashlib.sha256()
		hashed.update(mixed.encode("utf-8"))
		return hashed.hexdigest()


	@property
	def hash(self) -> str:
		return self.get_hash(self.token)


