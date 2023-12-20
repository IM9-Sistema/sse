import sys, types

m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
setattr(m, 'range', range)
sys.modules['kafka.vendor.six.moves'] = m

import time
from fastapi import FastAPI
from routes import get_routers
from libs.workers.data import PositionGather, AlertsGather, ProcessAlerts, ProcessNotations
from libs.workers.kafka_worker import KafkaPublish
import logging
import pyding

logging.basicConfig(level=logging.INFO)
app = FastAPI()
for router in get_routers():
	app.include_router(router)

PositionGather.begin()
AlertsGather.begin()
ProcessAlerts.begin()
ProcessNotations.begin()
KafkaPublish.begin()