import logging
import sys


def finalizar_programa_error(mensagem_erro: str):
    logging.error(f'{mensagem_erro}')
    sys.exit(1)
