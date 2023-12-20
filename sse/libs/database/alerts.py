from .connector import Database
from libs.structures import DatabaseType

database: Database = None

@Database.context(DatabaseType.EVENTOS, lower_case_columns=True)
def get_alert_info(alert_id: int):
	data= database.select("""
		SELECT
			*
		FROM EVENTOS_SISTEMA
		WHERE ID = ?
         """, [alert_id])
	return data[0] if data else None


@Database.context(DatabaseType.EVENTOS, lower_case_columns=True)
def get_notation_info(notation_id: int):
	data= database.select("""
		SELECT
			*
		FROM TB_SISTEMA_TRATATIVAS
		WHERE CD_REGISTRO_TRATATIVAS = ?
         """, [notation_id])
	return data[0] if data else None

