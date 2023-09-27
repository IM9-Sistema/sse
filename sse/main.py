from fastapi import FastAPI
from routes import positions, alerts
from libs.workers.data import PositionWorker, AlertWorker
import logging
import pyding


logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(positions.router)
app.include_router(alerts.router)
PositionWorker.begin()
AlertWorker.begin()