import logging
from typing import List
from app.utils.exceptions import finalizar_programa_error
from app.dto.models import Funcionario, ArquivoRetorno, DetalheArquivo
from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario

LISTA_FUNCIONARIOS_COM_COMPROVANTE = {}
LISTA_FUNCIONARIOS_SEM_COMPROVANTE_1 = {}
LISTA_FUNCIONARIOS_SEM_COMPROVANTE_2 = {}


def iniciar_processamento():
    validar_arquivos_existentes()
    funcionarios_liquido_folha_por_filial = carregar_lista_funcionarios_liquido_folha()
    lista_arquivos_retorno_bancario = carregar_retornos_bancario()

    if len(funcionarios_liquido_folha_por_filial) > 0 < len(lista_arquivos_retorno_bancario):
        logging.info('Liquido Folha e Retorno bancario carregados com sucesso!')
    else:
        finalizar_programa_error('Nenhum dado encontrado no Liquido Folha e/ou Retorno bancario, favor verificar!')

    percorrer_lista_filiais_liquido_folha(funcionarios_liquido_folha_por_filial, lista_arquivos_retorno_bancario)


def percorrer_lista_filiais_liquido_folha(funcionarios_liquido_folha_por_filial: dict,
                                          lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
    # flf = funcionario liquido folha
    for flf_codigo_filial in funcionarios_liquido_folha_por_filial:
        funcionarios_filial = funcionarios_liquido_folha_por_filial[flf_codigo_filial]

        percorrer_arquivos_retorno_bancario(flf_codigo_filial, funcionarios_filial,
                                            lista_arquivos_retorno_bancario)


def percorrer_arquivos_retorno_bancario(codigo_filial: str, funcionarios_liquido_folha: List[Funcionario],
                                        lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
    global LISTA_FUNCIONARIOS_SEM_COMPROVANTE_1, LISTA_FUNCIONARIOS_SEM_COMPROVANTE_2, \
        LISTA_FUNCIONARIOS_COM_COMPROVANTE

    for arquivo_retorno in lista_arquivos_retorno_bancario:

        # o PRIMEIRO arquivo da lista será percorrido sempre pela lista de funcionarios do liquido folha
        if lista_arquivos_retorno_bancario.index(arquivo_retorno) == 0:
            # flf = funcionario liquido folha
            for flf in funcionarios_liquido_folha:
                percorrer_lista_detalhe_lote(flf, arquivo_retorno.lote.detalhe, 1)

        if len(LISTA_FUNCIONARIOS_SEM_COMPROVANTE_1) > 0:
            LISTA_FUNCIONARIOS_SEM_COMPROVANTE_2 = {}
            # TODO: fazer a logica para percorrer essa lista, encontrar os funcionariios e preencher lista de sucesso e erro

        if len(LISTA_FUNCIONARIOS_SEM_COMPROVANTE_2) > 0:
            LISTA_FUNCIONARIOS_SEM_COMPROVANTE_1 = {}
            # TODO: fazer a logica para percorrer essa lista, encontrar os funcionariios e preencher lista de sucesso e erro


def percorrer_lista_detalhe_lote(funcionario: Funcionario, detalhes_lote: List[DetalheArquivo],
                                 num_lista_sem_comprovante: int):
    for detalhe in detalhes_lote:
        # TODO: fazer a logica para salvar funcionarios que foram encontrados e os que nao existem
        print(detalhe)


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()
