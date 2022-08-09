import os.path
from app.utils.exceptions import finalizar_programa_error


def validar_diretorio_liquido_folha():
    lista_arquivos_liquido_folha = os.listdir('../resources/entrada/liquido_folha/')
    if len(lista_arquivos_liquido_folha) != 1:
        finalizar_programa_error(f'Deve conter UM arquivo dentro da pasta resources/entrada/liquido_folha')


def validar_diretorio_retorno_bancario():
    lista_arquivos_liquido_folha = os.listdir('../resources/entrada/retorno_bancario/')
    if len(lista_arquivos_liquido_folha) <= 0:
        finalizar_programa_error(f'Nao foram encontrados retornos bancarios para processar os comprovantes')


def validar_arquivo_existe(endereco_arquivo: str):
    if not os.path.isfile(endereco_arquivo):
        finalizar_programa_error(f'Nenhum arquivo encontrado: {endereco_arquivo}')
