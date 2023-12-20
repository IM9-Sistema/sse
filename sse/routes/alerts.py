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

logger = logging.getLogger('uvicorn')

router = APIRouter(prefix='/alerts')

conversion_table = {
    "CD_REGISTRO_TRATATIVAS": "id_notation",
    "CD_ATENDIMENTO": "alert_id",
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

def queue_alerts(queue, alert_id = None, events: list = None):
    tracker_data = {}
    if alert_id is not None:
        yield f'id: -1\nevent: fetching_data\nalert_id: {alert_id}\ndata: {{}}\n\n'
        while True:
            try:
                tracker_data = trackers.get_tracker_info_by_event(alert_id)
                break
            except:
                logger.critical(f"Failed to fetch info for alert {alert_id}")
                continue
        yield f'id: -1\nevent: data_fetched\nalert_id: {alert_id}\ndata: {tracker_data}\n\n'

    yield f'id: -1\nevent: connected\nalert_id: {alert_id}\ndata: {{}}\n\n'
    last_data = {}
    while True:
        try:
            
            data = queue.get(timeout=5)
            message: dict = data['message']

            match message:
                case {"event": "alert_update"|"alert_create"|"alert_delete"|"notation_create"|"notation_delete"|"notation_update" as _event, "data": _data}:
                    event = _event
                    output = _data
                case {"event": "anchor", "type": _type, "rastreavel_id": _rastr, "user_id": _user_id, "data": _data}:
                    event = f"anchor_{_type}"
                    output = {"id_rastreavel": _rastr, "data": _data}
                
                case {"event": 'contacts', 'type': "insert"|"update" as type, "data": [{"id": id, "nome": nome, "fone": fone, "id_veiculo": id_veiculo, "ativo": active}, *_l],  **_d}:
                    event = f"contacts_{type}"
                    output = {"id": id, "name": nome, "phone": fone, "id_vehicle": id_veiculo, "active": active}
                
                case {"event": 'contacts', 'type': "delete" as type, "id_veiculo": id_veiculo, "id": id, **_d}:
                    event = f"contacts_{type}"
                    output = {"id": id}

                case _:
                    event = 'unknown_event'
                    output = message
            output = convert(output) if isinstance(output, dict) else output
            if (events is not None and 'event_id' in output and output['event_id'] not in events)\
            or ('id_rastreavel' in tracker_data and "id_rastreavel" in output and output["id_rastreavel"] != tracker_data['id_rastreavel'])\
            or ('id_veiculo' in tracker_data and "id_veiculo" in output and output["id_veiculo"] != tracker_data['id_veiculo'])\
            or (alert_id is not None and "alert_id" in output and output["alert_id"] != alert_id):

                yield f"id: {data['id']}\nevent: event-skip-notice\nskipped: {event}\nmeta-event-id: {output['event_id'] if 'event_id' in output else 'Not defined.'}\ndata: {{}}\n\n"
                continue
            yield f"id: {data['id']}\n"
            yield f"event: {event}\n"
            yield f"data: {json.dumps(output)}\n\n"
        except Empty:
            pass



@router.get('/',
            responses={
                200: {
                    'content': {
                        'text/event-stream': "id: int\nevent: eventname\ndata: {}\n\n"
                    },
                    'description': 'Depricated. use /subscribe'
                }
            }
        )
@router.get('/subscribe',
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
                     token: str, \
                     id: int = None,
                     type: int = None):
    events = {
        1: [2],
        2: [13, 16],
        3: [1,3,4,5,6,7,8,9,10,11,12,14,15],
        4: [105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161,162]
    }
    if type is not None and type not in events:
        raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail='Invalid event-package id.'
    )
    # Setup handler
    current_user = int(get_current_user(token))
    while True:
        try:
            user_data = users.get_user(current_user)
            break
        except Exception as e:
            logger.fatal(f"{e} - {current_user} - get_user")
            continue
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

    return StreamingResponse(queue_alerts(queue, id, events[type] if type else None), media_type="text/event-stream")