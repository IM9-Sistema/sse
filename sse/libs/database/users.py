from .connector import Database
from libs.structures import DatabaseType

database: Database = None

@Database.context(DatabaseType.PRODUCAO, lower_case_columns=True)
def get_user(user_id: int):
    return database.select("""
                        SELECT
                           ID_NIVEL_ACESSO,
                           NM_NOME
                        FROM CADASTRO_USUARIO
                        WHERE CD_REGISTRO_USUARIO = ?
                           """, [user_id])[0]