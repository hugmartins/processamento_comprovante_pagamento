import logging
import os.path
import csv
from typing import List

from app.utils.exceptions import finalizar_programa_error
from decimal import Decimal
from app.dto.models import Funcionario, ArquivoRetorno

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
        finalizar_programa_error(f'Nao foram encontrados retornos bancarios para processar os comprovantes')


def validar_arquivo_existe(endereco_arquivo: str):
    if not os.path.isfile(endereco_arquivo):
        finalizar_programa_error(f'Nenhum arquivo encontrado: {endereco_arquivo}')


def buscar_endereco_arquivo_liquido_folha():
    logging.info("Carregando arquivo liquido folha")

    nome_arq_liquido_folha = os.listdir(DIR_LIQUIDO_FOLHA)[0]
    arq_liquido_folha = os.path.join(DIR_LIQUIDO_FOLHA, nome_arq_liquido_folha)

    return arq_liquido_folha


def carregar_lista_funcionarios_liquido_folha() -> dict:
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


# TODO: remover index (usado apenas para conferencia)
def adicionar_funcionario_map_liquido_folha(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_LIQUIDO_FOLHA:
        lista_funcionarios_filial = MAP_LIQUIDO_FOLHA[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_LIQUIDO_FOLHA[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_LIQUIDO_FOLHA[codigo_filial] = [funcionario]


def carregar_retornos_bancario() -> List[ArquivoRetorno]:
    try:
        lista_retornos_bancario = os.listdir(DIR_RETORNO_BANCARIO)

        for nome_arquivo in lista_retornos_bancario:
            arq_retorno = os.path.join(DIR_RETORNO_BANCARIO, nome_arquivo)
            with open(arq_retorno, "r") as arquivo:
                dados_retorno_bancario = arquivo.readlines()

                for linha_arquivo_retorno in dados_retorno_bancario:
                    print(linha_arquivo_retorno)
                    break

        return []
    except Exception as error:
        finalizar_programa_error(f"Ocorreu um erro ao tentar carregar arquivo de retorno bancario: {error}")
