import logging
from typing import List
from utils.exceptions import finalizar_programa_error
from utils.utils import formatar_data_str
from dto.models import Funcionario, ArquivoRetorno, ComprovantePagamentoFuncionario
from service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario, excluir_datasources_existentes
from service.relatorio_service import gerar_relatorio_comprovante, gerar_relatorio_resultado_processamento

MAP_TOTAL_FUNCIONARIOS_POR_FILIAL = {}
MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL = {}
MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL = {}

LISTA_CPF_COM_COMPROVANTE = []
LISTA_CPF_SEM_COMPROVANTE = []


INCREMENTE_MAIS_UM = 1


def iniciar_processamento():
    validar_arquivos_existentes()
    excluir_datasources_existentes()
    funcionarios_liquido_folha = carregar_lista_funcionarios_liquido_folha()
    lista_arquivos_retorno_bancario = carregar_retornos_bancario()

    logging.info(f'Total funcionarios liquido folha: {len(funcionarios_liquido_folha)}')
    logging.info(f'Total arquivos de retorno bancario: {len(lista_arquivos_retorno_bancario)}')

    if len(funcionarios_liquido_folha) > 0 < len(lista_arquivos_retorno_bancario):
        logging.info('Liquido Folha e Retorno bancario carregados com sucesso!')
    else:
        finalizar_programa_error('Nenhum dado encontrado no Liquido Folha e/ou Retorno bancario, favor verificar!')

    localizar_dados_comprovante_funcionario(funcionarios_liquido_folha, lista_arquivos_retorno_bancario)

    logging.info(f'funcionarios COM comprovante: {len(LISTA_CPF_COM_COMPROVANTE)}')
    logging.warning(f'funcionarios SEM comprovante: {len(LISTA_CPF_SEM_COMPROVANTE)}')

    gerar_relatorio_comprovante(MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL)

    map_quantidade_comprovantes_por_filial = transformar_map_funcionarios_com_comprovante_por_filial()
    gerar_relatorio_resultado_processamento(MAP_TOTAL_FUNCIONARIOS_POR_FILIAL, map_quantidade_comprovantes_por_filial,
                                            MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL)


def transformar_map_funcionarios_com_comprovante_por_filial() -> dict:
    map_quantidade_comprovantes_por_filial = {}
    for codigo_filial in MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL:
        lista_funcionarios = MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial]
        map_quantidade_comprovantes_por_filial[codigo_filial] = len(lista_funcionarios)

    return map_quantidade_comprovantes_por_filial


def localizar_dados_comprovante_funcionario(funcionarios_liquido_folha: List[Funcionario],
                                            lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
    for funcionario in funcionarios_liquido_folha:
        comprovante_encontrado = False
        contabilizar_quantidade_funcionarios_por_filial(funcionario.descricao_filial)
        for arquivo_retorno in lista_arquivos_retorno_bancario:
            for detalhe in arquivo_retorno.lote.detalhe:
                if funcionario.cpf in detalhe.segmento_b.numero_inscricao_favorecido:
                    comprovante_encontrado = True

                    data_geracao_arquivo = formatar_data_str(
                        data_str=arquivo_retorno.header_arquivo.data_geracao_arquivo_str,
                        formato_entrada='%d/%m/%Y',
                        formato_saida='%Y%m'
                    )

                    funcionario.dados_comprovante = ComprovantePagamentoFuncionario(
                        nome_empresa_pagadora=arquivo_retorno.header_arquivo.nome_empresa,
                        data_geracao_arquivo_comprovante=data_geracao_arquivo,
                        detalhe_comprovante=detalhe
                    )
                    adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario)

        if comprovante_encontrado is False:
            adicionar_funcionario_lista_funcionario_sem_comprovante_por_filial(funcionario)


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()


def adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL:
        lista_funcionarios_filial = MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial] = [funcionario]

    LISTA_CPF_COM_COMPROVANTE.append(funcionario.cpf)


def adicionar_funcionario_lista_funcionario_sem_comprovante_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL:
        lista_funcionarios_filial = MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL[codigo_filial] = [funcionario]

    LISTA_CPF_SEM_COMPROVANTE.append(funcionario.cpf)


def contabilizar_quantidade_funcionarios_por_filial(nome_filial: str):
    codigo_filial = nome_filial.split("-")[0]
    if codigo_filial in MAP_TOTAL_FUNCIONARIOS_POR_FILIAL:
        quantidade_funcionarios_filial = int(MAP_TOTAL_FUNCIONARIOS_POR_FILIAL[codigo_filial]["quantidade_funcionario"])
        MAP_TOTAL_FUNCIONARIOS_POR_FILIAL[codigo_filial]["quantidade_funcionario"] = \
            quantidade_funcionarios_filial + INCREMENTE_MAIS_UM
    else:
        MAP_TOTAL_FUNCIONARIOS_POR_FILIAL[codigo_filial] = {
            "nome_filial": nome_filial, "quantidade_funcionario": INCREMENTE_MAIS_UM
        }
