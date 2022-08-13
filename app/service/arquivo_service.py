import logging
import os.path
import csv
from typing import List

from app.utils.exceptions import finalizar_programa_error
from decimal import Decimal
from app.dto.models import Funcionario, ArquivoRetorno, HeaderArquivo, TrailerArquivo, SegmentoA, SegmentoB, \
    DetalheArquivo, TipoRegistro, TrailerLote, Lote

DIR_LIQUIDO_FOLHA = '../resources/entrada/liquido_folha/'
DIR_RETORNO_BANCARIO = '../resources/entrada/retorno_bancario/'

MAP_LIQUIDO_FOLHA = {}


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


def carregar_lista_funcionarios_liquido_folha() -> dict:
    logging.info('Carregando dados do arquivo Liquido Folha.')
    try:
        with open(buscar_endereco_arquivo_liquido_folha(), 'r') as arquivo:
            dados_liquido_folha = csv.reader(arquivo, delimiter=';')

            # pular cabeçalho
            next(dados_liquido_folha, None)
            for linha in dados_liquido_folha:
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

                adicionar_funcionario_map_liquido_folha(funcionario)

        return MAP_LIQUIDO_FOLHA
    except Exception as error:
        finalizar_programa_error(f"Ocorreu um erro ao tentar carregar arquivo Liquido folha: {error}.")


def adicionar_funcionario_map_liquido_folha(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_LIQUIDO_FOLHA:
        lista_funcionarios_filial = MAP_LIQUIDO_FOLHA[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_LIQUIDO_FOLHA[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_LIQUIDO_FOLHA[codigo_filial] = [funcionario]


def carregar_retornos_bancario() -> List[ArquivoRetorno]:
    logging.info('Carregando dados dos arquivo de retorno bancario.')
    try:
        lista_arquivos_retorno = []
        arquivos_retornos_bancario = os.listdir(DIR_RETORNO_BANCARIO)

        for nome_arquivo in arquivos_retornos_bancario:
            arq_retorno = os.path.join(DIR_RETORNO_BANCARIO, nome_arquivo)
            with open(arq_retorno, "r") as arquivo:
                conteudo_arq_retorno = gerar_arquivo_retorno(arquivo.readlines())
                lista_arquivos_retorno.append(conteudo_arq_retorno)

        return lista_arquivos_retorno
    except Exception as error:
        finalizar_programa_error(f"Ocorreu um erro ao tentar carregar arquivo de retorno bancario: {error}.")


def gerar_arquivo_retorno(dados_retorno_bancario: List[str]) -> ArquivoRetorno:
    lista_detalhes = []

    for registro in dados_retorno_bancario:
        # print(registro)
        tipo_registro = int(registro[7:8])

        if tipo_registro == TipoRegistro.HEADER_ARQUIVO.value[0]:
            header_arqui = gerar_header_arquivo(registro)
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
        header_arquivo=header_arqui,
        lote=Lote(detalhe=lista_detalhes, trailer_lote=trailer_lote),
        trailer_arquivo=trailer_arquivo

    )


def gerar_header_arquivo(registro: str) -> HeaderArquivo:
    return HeaderArquivo(
        banco="",
        lote=0,
        tipo_registro=0,
        numero_inscricao_empresa="",
        nome_empresa="",
        codigo_remessa_retorno=2,
        data_geracao_arquivo_str="12082022",
        hora_geracao_arquivo_str=""

    )


def gerar_trailer_arquivo(registro: str) -> TrailerArquivo:
    return TrailerArquivo(
        quantidade_registro=0,
        tipo_registro=0

    )


def gerar_segmento_a(registro: str) -> SegmentoA:
    return SegmentoA(
        tipo_registro=0,
        codigo_segmento="",
        codigo_banco_favorecido="",
        agencia="",
        digito_verificador_agencia="",
        numero_conta="",
        digito_verificador_conta="",
        digito_verificador_ag_conta="",
        nome_favorecido="",
        numero_documento="",
        data_pagamento_str="12082022",
        valor_pagamento_str="000000000207777",
        nosso_numero="",
        data_real_efetivacao_pagamento_str="12082022",
        valor_real_efetivacao_pagamento_str="000000000207777"

    )


def gerar_segmento_b(registro: str) -> SegmentoB:
    return SegmentoB(
        tipo_registro=0,
        codigo_segmento="",
        numero_inscricao_favorecido=""

    )


def gerar_trailer_lote(registro: str) -> TrailerLote:
    return TrailerLote(
        quantidade_registro=0,
        tipo_registro=0,
        total_pago_lote=""

    )
