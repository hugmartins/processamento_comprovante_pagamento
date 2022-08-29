import json
import logging
from typing import List
from utils.exceptions import finalizar_programa_error
from utils.utils import formatar_data_str
from dto.models import Funcionario, ArquivoRetorno, ComprovantePagamentoFuncionario
from dto.enums import TipoArquivoProcessamento
from service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_folha_pagamento, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario, validar_diretorio_retorno_previa_pagamento
from service.relatorio_service import gerar_relatorio_comprovante, gerar_relatorio_resultado_processamento

MAP_TOTAL_FUNCIONARIOS_POR_FILIAL = {}
MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL = {}
MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL = {}
MAP_FUNCIONARIOS_INCOSISTENTES_POR_FILIAL = {}

TOTAL_FUNCIONARIOS_COM_COMPROVANTE = 0
TOTAL_FUNCIONARIOS_SEM_COMPROVANTE = 0


INCREMENTE_MAIS_UM = 1


def iniciar_processamento(opcao_processamento: int):
    validar_diretorio_liquido_folha()
    funcionarios_liquido_folha = carregar_lista_funcionarios_liquido_folha()

    if len(funcionarios_liquido_folha) > 0:
        logging.info(f'Liquido Folha com sucesso! Total funcionarios: {len(funcionarios_liquido_folha)}')
    else:
        finalizar_programa_error('Nenhum dado encontrado no Liquido Folha, favor verificar!')

    switch_processamento(opcao_processamento, funcionarios_liquido_folha)


def switch_processamento(opcao_processamento: int, funcionarios_liquido_folha: List[Funcionario]):
    if opcao_processamento == TipoArquivoProcessamento.COMPROVANTE_PAGAMENTO.value:
        processar_comprovante_pagamento(funcionarios_liquido_folha)
    elif opcao_processamento == TipoArquivoProcessamento.PREVIA_PAGAMENTO.value:
        processar_previa_pagamento(funcionarios_liquido_folha)


def processar_previa_pagamento(funcionarios_liquido_folha: List[Funcionario]):
    validar_diretorio_retorno_previa_pagamento()
    lista_arquivos_previa_pagamento = carregar_retornos_bancario(TipoArquivoProcessamento.PREVIA_PAGAMENTO)

    if len(lista_arquivos_previa_pagamento) > 0:
        logging.info(f'Retornos previa pagamentos carregados com sucesso! '
                     f'Total arquivos de retorno: {len(lista_arquivos_previa_pagamento)}')
    else:
        finalizar_programa_error('Nenhum dado encontrado no retorno previa pagamento, favor verificar!')

    buscar_inconsistencia_pagamento_funcionario(funcionarios_liquido_folha, lista_arquivos_previa_pagamento)
    print(json.dumps(MAP_FUNCIONARIOS_INCOSISTENTES_POR_FILIAL, default=lambda o: o.__dict__, ))


def processar_comprovante_pagamento(funcionarios_liquido_folha: List[Funcionario]):
    validar_diretorio_retorno_folha_pagamento()
    lista_arquivos_retorno_bancario = carregar_retornos_bancario(TipoArquivoProcessamento.COMPROVANTE_PAGAMENTO)

    if len(lista_arquivos_retorno_bancario) > 0:
        logging.info(f'Retornos comprovante pagamento carregados com sucesso! '
                     f'Total arquivos de retorno: {len(lista_arquivos_retorno_bancario)}')
    else:
        finalizar_programa_error('Nenhum dado encontrado no retorno comprovante pagamento, favor verificar!')

    burcar_comprovante_funcionario(funcionarios_liquido_folha, lista_arquivos_retorno_bancario)

    logging.info(f'funcionarios COM comprovante: {TOTAL_FUNCIONARIOS_COM_COMPROVANTE}')
    logging.warning(f'funcionarios SEM comprovante: {TOTAL_FUNCIONARIOS_SEM_COMPROVANTE}')

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


def burcar_comprovante_funcionario(funcionarios_liquido_folha: List[Funcionario],
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


def buscar_inconsistencia_pagamento_funcionario(funcionarios_liquido_folha: List[Funcionario],
                                                lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
    for funcionario in funcionarios_liquido_folha:
        for arquivo_retorno in lista_arquivos_retorno_bancario:
            for detalhe in arquivo_retorno.lote.detalhe:
                if funcionario.cpf in detalhe.segmento_b.numero_inscricao_favorecido:
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
                    adicionar_funcionario_lista_inconsistencias_pagamento_por_filial(funcionario)


def adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL:
        lista_funcionarios_filial = MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_FUNCIONARIOS_COM_COMPROVANTE_POR_FILIAL[codigo_filial] = [funcionario]

    global TOTAL_FUNCIONARIOS_COM_COMPROVANTE
    TOTAL_FUNCIONARIOS_COM_COMPROVANTE += 1


def adicionar_funcionario_lista_funcionario_sem_comprovante_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL:
        lista_funcionarios_filial = MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL[codigo_filial] = [funcionario]

    global TOTAL_FUNCIONARIOS_SEM_COMPROVANTE
    TOTAL_FUNCIONARIOS_SEM_COMPROVANTE += 1


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


def adicionar_funcionario_lista_inconsistencias_pagamento_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_FUNCIONARIOS_INCOSISTENTES_POR_FILIAL:
        lista_funcionarios_filial = MAP_FUNCIONARIOS_INCOSISTENTES_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_FUNCIONARIOS_INCOSISTENTES_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_FUNCIONARIOS_INCOSISTENTES_POR_FILIAL[codigo_filial] = [funcionario]
