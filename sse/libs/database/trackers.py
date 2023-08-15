from .connector import Database
from libs.structures import DatabaseType

database: Database = None

@Database.context(DatabaseType.PRODUCAO)
def get_trackers(client_id: int, user_id: int):
    print(f"{user_id!r}, {client_id!r}")
    data = database.select(f"""
                    DECLARE @USUARIO int = ?;
                    {'DECLARE @CLIENTE int = ?;' if client_id else ''}
                    SELECT
                        gar.ID_RASTREAVEL
                    FROM GRID_ATIVADOS_RASTREAMENTO AS gar
                    LEFT OUTER JOIN CADASTRO_USUARIO AS cau
                        ON cau.CD_REGISTRO_USUARIO = @USUARIO
                    WHERE (
                            cau.ID_NIVEL_ACESSO > 0
                            OR
                            (
                                (cau.VL_FILTRO_GRIDS_RASTREAVEIS = 1 AND gar.ID_RASTREAVEL IN (select cup.CD_RASTREAVEL from CADASTRO_USUARIO_PLACA cup WHERE cup.CD_USUARIO = @USUARIO))
                                OR
                                (cau.VL_FILTRO_GRIDS_RASTREAVEIS = 0 AND
                                    (gar.ID_CLIENTE IN (SELECT CD_CLIENTE FROM CLIENTES_POR_USUARIO WHERE CD_USUARIO = @USUARIO)
                                    OR gar.ID_CLIENTE_INSTALADO IN (SELECT CD_CLIENTE FROM CLIENTES_POR_USUARIO WHERE CD_USUARIO = @USUARIO)
                                    )
                                )
                                )
                        ) {'AND (ID_CLIENTE = @CLIENTE OR ID_CLIENTE_INSTALADO = @CLIENTE)' if client_id else ''}
                    """, [user_id, *[client_id if client_id else []]])
    return [str(i['ID_RASTREAVEL']) for i in data]