from fastapi import Depends, HTTPException, Query, status
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
import pyding
from pyding.structures import QueuedHandler
from libs.auth import get_current_user
import json
from libs.structures import TokenData
from libs.database import trackers, users
from queue import Queue, Empty
from typing import Annotated, List
import logging
import fastapi

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/alerts')

conversion_table = {
    "CD_REGISTRO_TRATATIVAS": "id_notation",
    "CD_ATENDIMENTO": "id_treatment",
    "CD_USUARIO": "id_user",
    "DT_TRATATIVA": "id_notation",
    "DS_TRATATIVA": "notation_text",
    "DS_POSICAO": "address",
    "VL_LATITUDE": "latitude",
    "VL_LONGITUDE": "longitude",
    "VL_VELOCIDADE": "speed",
    "CD_REGISTRO_SISTEMA": "alert_id",
    "DT_CADASTRO": "created_when",
    "CD_USUARIO_CRIOU": "created_user_id",
    "VL_STATUS": "status_id",
    "DT_PROCESSADO": "processed_when",
    "VL_PROCESSADO": "processed_value",
    "DT_CONFIRMACAO_PROCESSAMENTO": "processed_confirmation_when",
    "DS_DESTINATARIO": "destinatario",
    "ID_RASTREAVEL": "tracked_id",
    "ID_EVENTO": "event_id",
    "VL_PRIORIDADE_EVENTO": "priority_id",
    "DS_EVENTO": "event_text",
    "DT_ULTIMO_TRATAMENTO": "last_treatment_when",
    "DT_REAGENDADA": "scheduled_to",
    "CD_USUARIO_BAIXOU": "user_closed_id",
    "DT_BAIXOU": "closed_when",
    "NM_ULTIMO_TRATAMENTO": "last_treatment",
    "DS_IGNICAO": "ignition",
    "CD_CLIENTE": "client_id",
    "CD_MOTORISTA": "driver_id",
    "CD_VEICULO": "vehicle_id",
    "CD_USUARIO_ULT_TRATAMENTO": "user_last_treatment_id",
    "ID_TIPO_EQUIPAMENTO": "equipment_id",
    "DS_TIPO_EQUIPAMENTO": "equipment",
    "VL_INVISIVEL": "invisible",
    "DS_FILE": "file",
    "CD_AREARISCO": "id_risk_area",
    "DS_TIPO_BLOQUEIO": "id_block_type",
    "CD_USUARIO_INICIA_TRAT": "user_init_id",
    "DS_TIPO_REDE": "network_type",
    "DS_MOTIVO": "reason"
}

def convert(data: dict):
    output = {}
    for k, v in data.items():
        if k in conversion_table:
            output[conversion_table[k]] = v
        else:
            output[k] = v
    return output

def queue_alerts(queue):
    yield 'id: -1\nevent: connected\ndata: {}\n\n'
    while True:
        try:
            
            data = queue.get(timeout=5)
            match data['message']:
                case {"schema": {"name": "database.eventos.EVENTOS.dbo.TB_SISTEMA.Envelope", **_sk}, "payload": {"op": "c", "before": None, "after": after, **_pk}, **_k}:
                    event = "alert_create"
                    output = after
                
                case {"schema": {"name": "database.eventos.EVENTOS.dbo.TB_SISTEMA.Envelope", **_sk}, "payload": {"op": "u", "before": before, "after": after, **_pk}, **_k}:
                    event = "alert_update"
                    output = after
                
                case {"schema": {"name": "database.eventos.EVENTOS.dbo.TB_SISTEMA_TRATATIVAS.Envelope", **_sk}, "payload": {"op": "u", "before": before, "after": after, **_pk}, **_k}:
                    event = "notation_update"
                    output = after
                
                case {"schema": {"name": "database.eventos.EVENTOS.dbo.TB_SISTEMA_TRATATIVAS.Envelope", **_sk}, "payload": {"op": "c", "before": None, "after": after, **_pk}, **_k}:
                    event = "notation_create"
                    output = after

                case _:
                    event = 'unknown_event'
                    output = data["message"]

            yield f"id: {data['id']}\n"
            yield f"event: {event}\n"
            yield f"data: {json.dumps({'data': convert(output)})}\n\n"
        except Empty:
            yield 'id: -1\nevent: keep-alive\ndata: {}\n\n'




@router.get('/',
            responses={
                200: {
                    'content': {
                        'text/event-stream': "id: int\nevent: eventname\ndata: {}\n\n"
                    },
                    'description': 'Returns a event-stream whenever an alerts changes'
                }
            }
        )
async def get_alerts(background_tasks: fastapi.background.BackgroundTasks, \
                        token: str):
    # Setup handler
    current_user = int(get_current_user(token))
    user_data = users.get_user(current_user)

    args = {}

    if user_data['id_nivel_acesso'] < 1:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not verify your authentication details.',
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )

    handler: QueuedHandler = pyding.queue('alerts.message', **args, return_handler=True)
    queue: Queue = handler.get_queue()

    def unregister(handler: QueuedHandler):
        logger.info(f"Closing handler ({handler})")
        handler.unregister()
    
    background_tasks.add_task(unregister, handler)

    return StreamingResponse(queue_alerts(queue), media_type="text/event-stream")