from datetime import datetime
from pydantic import BaseModel, Field
from enum import StrEnum
from .session import Session

__version__ = '2.0.0/RC'

class CommandType(StrEnum):
	ALERT_UPDATE = "alert_update"
	ALERT_CREATE = "alert_create"
	ALERT_DELETE = "alert_delete"
	NOTATION_CREATE = "notation_create"
	NOTATION_DELETE = "notation_delete"
	NOTATION_UPDATE = "notation_update"

class Command(BaseModel):
	command_id: CommandType
	data: dict
	origin: Session|None = None
