import logging
from app.utils.exceptions import finalizar_programa_error
from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario


def iniciar_processamento():
    validar_arquivos_existentes()
    lista_funcionarios_liquido_folha = carregar_lista_funcionarios_liquido_folha()
    lista_arquivos_retorno_bancario = carregar_retornos_bancario()

    if len(lista_funcionarios_liquido_folha) > 0 < len(lista_arquivos_retorno_bancario) :
        logging.info('Liquido Folha e Retorno bancario carregados com sucesso!')
    else:
        finalizar_programa_error('Nenhum dado encontrado no Liquido Folha e/ou Retorno bancario, favor verificar!')


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()
