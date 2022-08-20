import logging
from typing import List
from app.utils.exceptions import finalizar_programa_error
from app.dto.models import Funcionario, ArquivoRetorno, DetalheArquivo
from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario
from app.service.relatorio_service import gerar_relatorio_comprovante

MAP_COMPROVANTE_FUNCIONARIO_POR_FILIAL = {}
MAP_FUNCIONARIOS_SEM_COMPROVANTE_POR_FILIAL = {}

LISTA_CPF_COM_COMPROVANTE = []
LISTA_CPF_SEM_COMPROVANTE = []


def iniciar_processamento():
    validar_arquivos_existentes()
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

    gerar_relatorio_comprovante(MAP_COMPROVANTE_FUNCIONARIO_POR_FILIAL)


def localizar_dados_comprovante_funcionario(funcionarios_liquido_folha: List[Funcionario],
                                            lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
    for funcionario in funcionarios_liquido_folha:
        comprovante_encontrado = False

        for arquivo_retorno in lista_arquivos_retorno_bancario:
            for detalhe in arquivo_retorno.lote.detalhe:
                if funcionario.cpf in detalhe.segmento_b.numero_inscricao_favorecido:
                    comprovante_encontrado = True
                    funcionario.dados_comprovante = detalhe
                    adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario)

        if comprovante_encontrado is False:
            adicionar_funcionario_lista_funcionario_sem_comprovante_por_filial(funcionario)


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()


def adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in MAP_COMPROVANTE_FUNCIONARIO_POR_FILIAL:
        lista_funcionarios_filial = MAP_COMPROVANTE_FUNCIONARIO_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        MAP_COMPROVANTE_FUNCIONARIO_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        MAP_COMPROVANTE_FUNCIONARIO_POR_FILIAL[codigo_filial] = [funcionario]

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
