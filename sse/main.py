from os import environ
import sys, types

# Some library shenanigans
m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
setattr(m, 'range', range)
sys.modules['kafka.vendor.six.moves'] = m

import time
from fastapi import FastAPI
from routes import get_routers
from libs.workers.data import PositionGather, AlertsGather, ProcessAlerts, ProcessNotations, EquipamentsGather
from libs.workers.kafka_worker import KafkaPublish
import logging
import pyding
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

logging.basicConfig(level=logging.getLevelNamesMapping()[environ.get('LOG_LEVEL')])
app = FastAPI()

# Load routes dynamically
for router in get_routers():
	app.include_router(router)

# Include Elastic's middleware
apm = make_apm_client({
    'SERVICE_NAME': 'FastAPI_SSE',
    'SECRET_TOKEN': environ.get('ELASTIC_APM_SECRET_TOKEN'),
    'SERVER_URL': environ.get('ELASTIC_APM_ADDRESS'),
    'LOG_LEVEL': environ.get('LOG_LEVEL'),
})

app.add_middleware(ElasticAPM, client=apm)

# Initialize Kafka Consumers
PositionGather.begin()
AlertsGather.begin()
ProcessAlerts.begin()
ProcessNotations.begin()
KafkaPublish.begin()
EquipamentsGather.begin()