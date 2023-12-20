from datetime import datetime
from pydantic import BaseModel

__version__ = '2.0.0/RC'

class Metadata[T](BaseModel):
	data: T|None
	emitted_by: str
	emitted_at: datetime
	details: str|None

	@classmethod
	def now(cls):
		return cls(
			data={},
			emitted_by=f"IM9/SSE {__version__}",
			emitted_at=datetime.utcnow(),
			details=None
		)
	