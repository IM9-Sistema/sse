from .connector import Database
from libs.structures import DatabaseType

database: Database = None

@Database.context(DatabaseType.EVENTOS, lower_case_columns=True)
def get_alert_info(alert_id: int):
	data= database.select("""
		SELECT
			evs.id as alert_id,
			evs.data_criacao as created_when,
			NULL as created_user_id,
			evs.id_status as status_id,
			evs.data_processado as processed_when,
			evs.processado as processed_value,
			NULL AS processed_confirmation_when,
			evs.destinatario,
			evs.id_rastreavel as tracked_id,
			evs.id_evento as event_id,
			NULL AS priority_id,
			evs.evento as event_text,
			tbs.DT_TRATATIVA as last_treatment_when,
			evs.data_reagendada as scheduled_to,
			evs.id_usuario_baixou as user_closed_id,
			evs.data_baixou as closed_when,
			tbs.DS_TRATATIVA as last_treatment,
			evs.posicao as address,
			evs.latitude,
			evs.longitude,
			evs.velocidade as speed,
			evs.ignicao as ignition,
			(CASE evs.id_cliente_instalado WHEN NULL THEN evs.id_cliente ELSE evs.id_cliente_instalado END) as client_id,
			NULL AS driver_id,
			id_veiculo as vehicle_id,
			id_usuario_ult_tratamento as user_last_treatment_id,
			usuario_ult_tratamento as user_last_treatment,
			id_equipamento as equipment_id,
			nome_equipamento as equipment,
			0 as invisible,
			NULL AS [file]
		FROM EVENTOS_SISTEMA AS evs
		LEFT OUTER JOIN TB_SISTEMA_TRATATIVAS AS tbs
			ON evs.id = tbs.CD_ATENDIMENTO and tbs.DT_TRATATIVA = (SELECT TOP 1 MAX(DT_TRATATIVA) FROM TB_SISTEMA_TRATATIVAS WHERE CD_ATENDIMENTO = evs.id)
		WHERE ID = ?
         """, [alert_id])
	return data[0] if data else None


@Database.context(DatabaseType.EVENTOS, lower_case_columns=True)
def get_notation_info(notation_id: int):
	data= database.select("""
		SELECT
			CD_REGISTRO_TRATATIVAS AS id_notation,
			CD_ATENDIMENTO AS alert_id,
			CD_USUARIO as id_user,
			DS_TRATATIVA AS notation_text,
			DS_POSICAO AS address,
			VL_LATITUDE AS latitude,
			VL_LONGITUDE AS longitude,
			VL_VELOCIDADE AS speed,
			DS_IGNICAO AS ignition,
			ID_EVENTO AS event_id
		FROM TB_SISTEMA_TRATATIVAS
		WHERE CD_REGISTRO_TRATATIVAS = ?
         """, [notation_id])
	return data[0] if data else None

