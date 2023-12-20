import time
from fastapi import FastAPI
from routes import get_routers
from libs.workers.data import PositionGather, AlertsGather, ProcessAlerts, ProcessNotations
import logging
import pyding

logging.basicConfig(level=logging.DEBUG)
app = FastAPI()
for router in get_routers():
	app.include_router(router)

PositionGather.begin()
AlertsGather.begin()
ProcessAlerts.begin()
ProcessNotations.begin()