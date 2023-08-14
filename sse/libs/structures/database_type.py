from enum import StrEnum


class DatabaseType(StrEnum):
    PRODUCAO = "producao"
    EVENTOS = "eventos"
    POSICAO = "posicao"
    FINANCEIRO = "financeiro"
    TELEMETRIA = "telemetria"
    VIRLOCK = "virlock"
    GETRAK = 'getrak'
    RELATORIOS = 'relatorios'
    IMAGENS = 'imagens'