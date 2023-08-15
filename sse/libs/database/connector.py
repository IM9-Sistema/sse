import collections
from os import environ
from typing import Any, Generator
from libs.structures import DatabaseType
from datetime import datetime, timedelta
from types import FunctionType, NoneType

import logging
import struct
import pyodbc

logger = logging.getLogger(__name__)


class Database(object):
    """
    Database
    ---------------
    Adiciona contexto de database à funções.
    """
    def __init__(self, function: FunctionType, database: DatabaseType|str, context: bool,\
                 dict_class: dict = dict, lower_case_columns: bool = None, nodes: bool = None, \
                 autocommit: bool = None):
        """
        function: Função para qual a classe dará contexto.
        database: Database para qual a classe irá conectar-se
        context: Se a classe dará o contexto `database` à função
        dict_class: Classe para formar os dicionários
        lower_case_columns: Retornar os nomes das colunas em minúsculo
        nodes: Gerar nodes a partir das colunas `{'usuario__id': 1, 'usuario__nome': 'João', 'id': 200}` -> `{'usuario': {'id': 1, 'nome': João'}, 'id': 200}`
        """
        self.function = function
        self.database = database
        self.context = context
        self.__globals = {'database': self}
        self.dict_class = dict_class
        self.connection: pyodbc.Connection = None
        self.lower_case_columns = lower_case_columns
        self.nodes = nodes
        self.autocommit = autocommit

    @property
    def __globals__(self):
        return self.__globals

    def close(self, dont_commit=None):
        if self.is_connected:
            logger.debug("Connection closed")
            if not dont_commit:
                self.connection.commit()
            self.connection.close()
        self.connection = None

    def connect(self):
        logger.debug("Connecting to database")
        self.connection = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"+
                                        f"SERVER={environ.get('DATABASE_HOST', '10.10.1.2')};"+
                                        f"DATABASE={self.database};"+
                                        f"UID={environ.get('DATABASE_USER', 'sa')};"+
                                        f"PWD={environ.get('DATABASE_PWD')};",
                                        autocommit=self.autocommit
                                        )
        logger.debug("Connected")

    @property
    def is_connected(self) -> bool:
        return self.connection != None

    def __call__(self, *args, **kwargs) -> Any:
        try:
            if self.context:
                self.function.__globals__.update(self.__globals)
                output = self.function(*args, **kwargs)
            else:
                output = self.function(*args, **kwargs, database=self)
        except Exception as e:
            self.rollback()
            self.close()
            raise e
        self.close()
        return output
    
    @staticmethod
    def nodefy(input: dict[str, Any]):
        def update(d, u):
            if not isinstance(d, collections.abc.Mapping): d = {}
            #print(d)
            for k, v in u.items():
                #print('k ', k, 'v ', v)
                if isinstance(v, collections.abc.Mapping):
                    d[k] = update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        output = {}
        for i in input.keys():
            if i.endswith("__") or "__" not in i:
                output[i] = input[i]
                continue
            tokens = i.split("__")
            token_data = {tokens[-1]: input[i]}
            for token in reversed(tokens[:-1]):
                token_data = {token: token_data}
            output = update(output, token_data)
        return output

    def rollback(self):
        logger.debug("Executando rollback")
        return self.connection.rollback()

    def query(self, sql: str, values: list[Any] = []) -> pyodbc.Cursor:
        if not self.is_connected:
            self.connect()
        logger.debug(sql)
        logger.debug(values)
        cursor: pyodbc.Cursor = self.connection.cursor()
        result = cursor.execute(sql, values)
        return result

    def stream_select(self, sql: str, values: list[Any] = []) -> Generator[dict[str, Any], NoneType, NoneType]:
        cursor: pyodbc.Cursor = self.query(sql, values)

        columns: list[str] = [c[0].lower() if self.lower_case_columns else c[0] for c in cursor.description]
        try:
            while row := cursor.fetchone():
                yield self.nodefy(self.dict_class(zip(columns, row))) if self.nodes else self.dict_class(zip(columns, row))
        except:
            pass
        self.close()

    

    def select(self, sql: str, values: list[Any] = []) -> list[dict[str, Any]]:
        cursor: pyodbc.Cursor = self.query(sql, values)

        columns: list[str] = [c[0].lower() if self.lower_case_columns else c[0] for c in cursor.description]
        rows: list[Any] = cursor.fetchall()
        results: list[dict[str, Any]] = [self.nodefy(self.dict_class(zip(columns, r))) if self.nodes else self.dict_class(zip(columns, r)) for r in rows ]
        logger.debug("Finished retrieving data")
        return results


    @classmethod
    def context(cls, database: DatabaseType|str = DatabaseType.PRODUCAO, dict_class=dict, lower_case_columns=None, nodes: bool=None, time_converter=None):
        def decorator(function):
            object = cls(function, database, True, dict_class, lower_case_columns, nodes, time_converter)
            object.__name__ = function.__name__
            return object
        return decorator

