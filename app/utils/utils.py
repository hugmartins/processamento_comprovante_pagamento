import logging
from datetime import datetime


def converter_string_data(data_string: str, formato: str = '%d/%m/%Y') -> datetime:
    try:
        return datetime.strptime(data_string, formato)
    except Exception as error:
        logging.error(f'Erro ao converter data {data_string} : {error}')


def data_atual_formatada(formato: str = '%d_%m_%Y') -> str:
    return datetime.now().strftime(formato)


def formatar_data(data: datetime, formato: str = '%d_%m_%Y') -> str:
    return data.strftime(formato)


def formatar_data_str(data_str: str, formato_entrada: str, formato_saida: str = '%d_%m_%Y') -> str:
    data = converter_string_data(data_str, formato_entrada)
    return data.strftime(formato_saida)
