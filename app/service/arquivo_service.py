import logging
import os.path
from app.utils.exceptions import finalizar_programa_error


DIR_LIQUIDO_FOLHA = '../resources/entrada/liquido_folha/'
DIR_RETORNO_BANCARIO = '../resources/entrada/retorno_bancario/'


def validar_diretorio_liquido_folha():
    lista_arquivos_liquido_folha = os.listdir(DIR_LIQUIDO_FOLHA)
    if len(lista_arquivos_liquido_folha) != 1:
        finalizar_programa_error(f'Deve conter UM arquivo do tipo .cvs dentro da pasta {DIR_LIQUIDO_FOLHA}')


def validar_diretorio_retorno_bancario():
    lista_arquivos_liquido_folha = os.listdir(DIR_RETORNO_BANCARIO)
    if len(lista_arquivos_liquido_folha) <= 0:
        finalizar_programa_error(f'Nao foram encontrados retornos bancarios para processar os comprovantes')


def validar_arquivo_existe(endereco_arquivo: str):
    if not os.path.isfile(endereco_arquivo):
        finalizar_programa_error(f'Nenhum arquivo encontrado: {endereco_arquivo}')


def carregar_endereco_arquivo_liquido_folha():
    logging.info("Carregando arquivo liquido folha")

    nome_arq_liquido_folha = os.listdir(DIR_LIQUIDO_FOLHA)[0]
    arq_liquido_folha = os.path.join(DIR_LIQUIDO_FOLHA, nome_arq_liquido_folha)

    return arq_liquido_folha
