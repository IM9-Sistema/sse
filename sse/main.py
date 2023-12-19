import time
from fastapi import FastAPI
from routes import get_routers
from libs.workers.data import PositionGather, AlertsGather
import logging
import pyding

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(), logging.FileHandler(f'{int(time.time())}.log')])
logging.getLogger('aiokafka').setLevel(logging.INFO)


app = FastAPI()
for router in get_routers():
	app.include_router(router)

PositionGather.begin()
AlertsGather.begin()