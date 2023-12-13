import time
from fastapi import FastAPI
from routes import positions, alerts
from libs.workers.data import PositionGather, AlertsGather
import logging
import pyding

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(), logging.FileHandler(f'{int(time.time())}.log')])
logging.getLogger('aiokafka.conn').setLevel(logging.NOTSET)
logging.getLogger('aiokafka.consumer.fecther').setLevel(logging.NOTSET)


app = FastAPI()
app.include_router(positions.router)
app.include_router(alerts.router)
PositionGather.begin()
AlertsGather.begin()