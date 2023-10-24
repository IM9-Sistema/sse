from fastapi import FastAPI
from routes import positions
from libs.workers.data import PositionGather, AlertsGather
import logging
import pyding


logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(positions.router)
PositionGather.begin()
AlertsGather.begin()