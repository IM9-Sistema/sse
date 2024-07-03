import pyodbc
from .connector import Database
from libs.structures import DatabaseType
import logging
logger = logging.getLogger('uvicorn')
database: Database = None


@Database.context(DatabaseType.EVENTOS, lower_case_columns=True)
def get_tracker_info_by_event(event_id):
	while True:
		try:
			data = database.select("SELECT DISTINCT ID_VEICULO, ID_RASTREAVEL, ID_CLIENTE, ID_CLIENTE_INSTALADO, ID_EQUIPAMENTO FROM FINANCEIRO.dbo.CADASTRO_ATIVACAO WHERE ID_RASTREAVEL = (SELECT ID_RASTREAVEL FROM EVENTOS.dbo.TB_SISTEMA WHERE CD_REGISTRO_SISTEMA = ?)", [event_id,])
			return data[0] if data else {}
		except pyodbc.Error as e:
			logger.fatal(f"{e} - {event_id} - get_tracker_info_by_event")
			continue

@Database.context(DatabaseType.PRODUCAO)
def get_trackers(client_id: int = None, user_id: int = None):
	print(f"{user_id!r}, {client_id!r}")
	values = []
	if user_id: values.append(user_id)
	if client_id: values.append(client_id)
	data = database.select(f"""
					DECLARE @USUARIO int = ?;
					{'DECLARE @CLIENTE int = ?;' if client_id else ''}
					SELECT
						gat.ID_RASTREAVEL
					FROM GRID_ATUAL_COMPLETO AS gat
					LEFT OUTER JOIN CADASTRO_USUARIO AS cau
						ON cau.CD_REGISTRO_USUARIO = @USUARIO
					WHERE

					(
							(cau.VL_CENTRAL = 1)
							OR (
									cau.VL_CENTRAL = 0
									AND (
												( -- FGR 1 && FCL 1
													(cau.VL_FILTRO_GRIDS_RASTREAVEIS = 1 AND cau.VL_FILTRO_CLIENTE = 1)
													AND
													gat.id_cliente = gat.id_cliente_instalado
													AND
													(select TOP 1 1 from CADASTRO_USUARIO_PLACA cup where cup.CD_USUARIO = cau.CD_REGISTRO_USUARIO AND cup.CD_RASTREAVEL = gat.ID_RASTREAVEL) = 1
												
												)
												OR
												( -- FGR 0 && FCL 1
													(cau.VL_FILTRO_GRIDS_RASTREAVEIS = 0 AND cau.VL_FILTRO_CLIENTE = 1)
													AND
													gat.id_cliente = gat.id_cliente_instalado
													
													AND
													(select TOP 1 1 from CLIENTES_POR_USUARIO cuc WHERE CUC.CD_USUARIO =cau.CD_REGISTRO_USUARIO AND cuc.CD_CLIENTE IN (gat.id_cliente, gat.id_cliente_instalado)) = 1
												
												)
												OR
												( -- FGR 1 && FCL 0
													(cau.VL_FILTRO_GRIDS_RASTREAVEIS = 1 AND cau.VL_FILTRO_CLIENTE = 0)
													--AND
													--gat.id_cliente = gat.id_cliente_instalado
													
													AND
													gat.ID_RASTREAVEL in (select CD_RASTREAVEL from CADASTRO_USUARIO_PLACA cup where cup.CD_USUARIO = cau.CD_REGISTRO_USUARIO AND cup.CD_RASTREAVEL = gat.ID_RASTREAVEL)
												
												)
												OR
												( -- FGR 0 && FCL 0
													(cau.VL_FILTRO_GRIDS_RASTREAVEIS = 0 AND cau.VL_FILTRO_CLIENTE = 0)
													AND
													(select TOP 1 1 from CLIENTES_POR_USUARIO cuc WHERE CUC.CD_USUARIO =cau.CD_REGISTRO_USUARIO AND cuc.CD_CLIENTE IN (gat.id_cliente, gat.id_cliente_instalado)) = 1
												)
									)
							)
					)

					{'AND (ID_CLIENTE = @CLIENTE OR ID_CLIENTE_INSTALADO = @CLIENTE)' if client_id else ''}
					""", values)
	return [i['ID_RASTREAVEL'] for i in data]