import logging
import os.path
import csv
import json
from typing import List
from decimal import Decimal

from utils.exceptions import finalizar_programa_error
from dto.models import Funcionario, ArquivoRetorno, HeaderArquivo, TrailerArquivo, SegmentoA, SegmentoB, \
    DetalheArquivo, TipoRegistro, TrailerLote, Lote, ReportComprovante, DetalheReportComprovante, \
    ReportResultadoProcessamento, DetalheReportResultadoProcessamento

DIR_LIQUIDO_FOLHA = '../recursos/liquido_folha/'
DIR_RETORNO_BANCARIO = '../recursos/retorno_bancario/'
DIR_DATASOURCE = '../jasper_report/datasource/'


def validar_diretorio_liquido_folha():
    lista_arquivos_liquido_folha = os.listdir(DIR_LIQUIDO_FOLHA)
    if len(lista_arquivos_liquido_folha) != 1:
        finalizar_programa_error(f'Deve conter UM arquivo do tipo .cvs dentro da pasta {DIR_LIQUIDO_FOLHA}')


def validar_diretorio_retorno_bancario():
    lista_arquivos_liquido_folha = os.listdir(DIR_RETORNO_BANCARIO)
    if len(lista_arquivos_liquido_folha) <= 0:
        finalizar_programa_error(f'Nao foram encontrados retornos bancarios para processar os comprovantes.')


def validar_arquivo_existe(endereco_arquivo: str):
    if not os.path.isfile(endereco_arquivo):
        finalizar_programa_error(f'Nenhum arquivo encontrado: {endereco_arquivo}')


def buscar_endereco_arquivo_liquido_folha():
    nome_arq_liquido_folha = os.listdir(DIR_LIQUIDO_FOLHA)[0]
    arq_liquido_folha = os.path.join(DIR_LIQUIDO_FOLHA, nome_arq_liquido_folha)

    return arq_liquido_folha


def carregar_lista_funcionarios_liquido_folha() -> List[Funcionario]:
    logging.info('Carregando dados do arquivo Liquido Folha.')
    lista_funcionarios_liquido_folha = []
    try:
        with open(buscar_endereco_arquivo_liquido_folha(), 'r') as arquivo:
            dados_liquido_folha = csv.reader(arquivo, delimiter=';')

            # pular cabeçalho
            next(dados_liquido_folha, None)
            for linha in dados_liquido_folha:
                if linha[6] == "BRADESCO":
                    funcionario = Funcionario(
                        descricao_filial=linha[0],
                        nome_completo=linha[1],
                        id_funcionario=linha[2],
                        cpf=linha[3],
                        agencia_salario=linha[4],
                        conta_salario=linha[5],
                        banco=linha[6],
                        src_total_verba=Decimal(linha[7].replace(".", "").replace(",", "."))
                    )

                    lista_funcionarios_liquido_folha.append(funcionario)

        return lista_funcionarios_liquido_folha
    except Exception as error:
        finalizar_programa_error(f"Ocorreu um erro ao tentar carregar arquivo Liquido folha: {error}.")


def carregar_retornos_bancario() -> List[ArquivoRetorno]:
    logging.info('Carregando dados dos arquivo de retorno bancario.')
    try:
        lista_arquivos_retorno = []
        arquivos_retornos_bancario = os.listdir(DIR_RETORNO_BANCARIO)

        for nome_arquivo in arquivos_retornos_bancario:
            arq_retorno = os.path.join(DIR_RETORNO_BANCARIO, nome_arquivo)
            dados_retorno_bancario = ler_arquivo_retorno(arq_retorno)

            primeira_linha = dados_retorno_bancario[0]
            if int(primeira_linha[0:3]) != 237 and int(primeira_linha[142:143]) != 2:
                finalizar_programa_error(f"Arquivo {arq_retorno} nao 'e arquivo de retorno do BRADESCO.")

            conteudo_arq_retorno = gerar_arquivo_retorno_bradesco(dados_retorno_bancario)
            lista_arquivos_retorno.append(conteudo_arq_retorno)

        return lista_arquivos_retorno
    except Exception as error:
        finalizar_programa_error(f"Ocorreu um erro ao tentar carregar arquivo de retorno bancario: {error}.")


def ler_arquivo_retorno(arquivo_retorno: str) -> List[str]:
    with open(arquivo_retorno, "r") as arquivo:
        return arquivo.readlines()


def gerar_arquivo_retorno_bradesco(dados_retorno_bancario: List[str]) -> ArquivoRetorno:
    lista_detalhes = []
    header_arquivo = None
    trailer_lote = None
    trailer_arquivo = None

    for registro in dados_retorno_bancario:
        tipo_registro = int(registro[7:8])

        if tipo_registro == TipoRegistro.HEADER_ARQUIVO.value[0]:
            header_arquivo = gerar_header_arquivo(registro)
        elif tipo_registro == TipoRegistro.DETALHE.value[0] and registro[13:14] == "A":

            segmento_a = gerar_segmento_a(registro)
            index_segmento_b = (dados_retorno_bancario.index(registro) + 1)
            registro_segmento_b = dados_retorno_bancario[index_segmento_b]
            segmento_b = None
            if registro_segmento_b[13:14] == "B":
                segmento_b = gerar_segmento_b(registro_segmento_b)

            lista_detalhes.append(DetalheArquivo(segmento_a=segmento_a, segmento_b=segmento_b))
        elif tipo_registro == TipoRegistro.TRAILER_LOTE.value[0]:
            trailer_lote = gerar_trailer_lote(registro)
        elif tipo_registro == TipoRegistro.TRAILER_ARQUIVO.value[0]:
            trailer_arquivo = gerar_trailer_arquivo(registro)

    return ArquivoRetorno(
        header_arquivo=header_arquivo,
        lote=Lote(detalhe=lista_detalhes, trailer_lote=trailer_lote),
        trailer_arquivo=trailer_arquivo

    )


def gerar_header_arquivo(registro: str) -> HeaderArquivo:
    return HeaderArquivo(
        banco=registro[0:3],
        lote=int(registro[3:7]),
        tipo_registro=int(registro[7:8]),
        numero_inscricao_empresa=registro[18:32],
        nome_empresa=registro[72:102],
        codigo_remessa_retorno=int(registro[142:143]),
        data_geracao_arquivo_str=registro[143:151],
        hora_geracao_arquivo_str=registro[151:157]

    )


def gerar_trailer_arquivo(registro: str) -> TrailerArquivo:
    return TrailerArquivo(
        quantidade_registro=int(registro[23:29]),
        tipo_registro=int(registro[7:8])

    )


def gerar_segmento_a(registro: str) -> SegmentoA:
    return SegmentoA(
        tipo_registro=int(registro[7:8]),
        codigo_segmento=registro[13:14],
        codigo_banco_favorecido=registro[20:23],
        agencia=registro[23:28],
        digito_verificador_agencia=registro[28:29],
        numero_conta=registro[29:41],
        digito_verificador_conta=registro[41:42],
        digito_verificador_ag_conta=registro[42:43],
        nome_favorecido=registro[43:73],
        numero_documento=registro[73:93],
        data_pagamento_str=registro[93:101],
        valor_pagamento_str=registro[119:134],
        nosso_numero=registro[134:154],
        data_real_efetivacao_pagamento_str=registro[154:162],
        valor_real_efetivacao_pagamento_str=registro[162:177]

    )


def gerar_segmento_b(registro: str) -> SegmentoB:
    return SegmentoB(
        tipo_registro=int(registro[7:8]),
        codigo_segmento=registro[13:14],
        numero_inscricao_favorecido=registro[18:32]

    )


def gerar_trailer_lote(registro: str) -> TrailerLote:
    return TrailerLote(
        quantidade_registro=int(registro[17:23]),
        tipo_registro=int(registro[7:8]),
        total_pago_lote=registro[23:41]

    )


def criar_arquivo_datasource_comprovante_pagamento(nome_arquivo: str, comprovantes_pagamento_filial: ReportComprovante):
    arquivo_datasource = os.path.join(DIR_DATASOURCE, f'{nome_arquivo}.csv')
    try:
        nome_atributos = list(DetalheReportComprovante.schema()["properties"].keys())

        with open(arquivo_datasource, "w") as datasource_csv:
            escritor = csv.DictWriter(datasource_csv, fieldnames=nome_atributos)
            escritor.writeheader()
            for detalhe_report in comprovantes_pagamento_filial.detalhe_report:
                escritor.writerow(json.loads(detalhe_report.json()))
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar datasource {nome_arquivo}. {error}')


def criar_arquivo_datasource_resultado_processamento(nome_arquivo: str,
                                                     resultado_processamento: ReportResultadoProcessamento):
    arquivo_datasource = os.path.join(DIR_DATASOURCE, f'{nome_arquivo}.csv')
    try:
        nome_atributos = list(DetalheReportResultadoProcessamento.schema()["properties"].keys())

        with open(arquivo_datasource, "w", encoding="utf-8") as datasource_csv:
            escritor = csv.DictWriter(datasource_csv, fieldnames=nome_atributos)
            escritor.writeheader()
            for resultado in resultado_processamento.detalhe_report:
                escritor.writerow(json.loads(resultado.json()))
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar datasource {nome_arquivo}. {error}')


def excluir_datasources_existentes():
    lista_datasources = os.listdir(DIR_DATASOURCE)
    for nome_arquivo_datasource in lista_datasources:
        datasource_para_exclusao = os.path.join(DIR_DATASOURCE, nome_arquivo_datasource)
        os.remove(datasource_para_exclusao)
