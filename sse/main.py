import time
from fastapi import FastAPI
from routes import positions, alerts
from libs.workers.data import PositionGather, AlertsGather
import logging
import pyding


logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(), logging.FileHandler(f'{int(time.time())}.log')])

app = FastAPI()
app.include_router(positions.router)
app.include_router(alerts.router)
PositionGather.begin()
AlertsGather.begin()