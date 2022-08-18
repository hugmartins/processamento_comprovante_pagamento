import logging
from typing import List
from app.utils.exceptions import finalizar_programa_error
from app.dto.models import Funcionario, ArquivoRetorno, DetalheArquivo
from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario

LISTA_COMPROVANTE_FUNCIONARIO_POR_FILIAL = {}
LISTA_FUNCIONARIOS_COM_COMPROVANTE = []
LISTA_FUNCIONARIOS_SEM_COMPROVANTE = []


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

    logging.info(f'funcionarios COM comprovante: {len(LISTA_FUNCIONARIOS_COM_COMPROVANTE)}')
    logging.warning(f'funcionarios SEM comprovante: {len(LISTA_FUNCIONARIOS_SEM_COMPROVANTE)}')


def localizar_dados_comprovante_funcionario(funcionarios_liquido_folha: List[Funcionario],
                                            lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
    for funcionario in funcionarios_liquido_folha:
        for arquivo_retorno in lista_arquivos_retorno_bancario:
            for detalhe in arquivo_retorno.lote.detalhe:
                if funcionario.cpf in detalhe.segmento_b.numero_inscricao_favorecido:
                    funcionario.dados_comprovante = detalhe
                    adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario)
                    LISTA_FUNCIONARIOS_COM_COMPROVANTE.append(funcionario.cpf)

        validar_funcionario_com_comprovante(funcionario)


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()


def adicionar_funcionario_lista_funcionario_comprovante_por_filial(funcionario: Funcionario):
    codigo_filial = funcionario.descricao_filial.split("-")[0]

    if codigo_filial in LISTA_COMPROVANTE_FUNCIONARIO_POR_FILIAL:
        lista_funcionarios_filial = LISTA_COMPROVANTE_FUNCIONARIO_POR_FILIAL[codigo_filial]
        lista_funcionarios_filial.append(funcionario)
        LISTA_COMPROVANTE_FUNCIONARIO_POR_FILIAL[codigo_filial] = lista_funcionarios_filial
    else:
        LISTA_COMPROVANTE_FUNCIONARIO_POR_FILIAL[codigo_filial] = [funcionario]


def validar_funcionario_com_comprovante(funcionario: Funcionario):
    if funcionario.cpf not in LISTA_FUNCIONARIOS_COM_COMPROVANTE:
        LISTA_FUNCIONARIOS_SEM_COMPROVANTE.append(funcionario)
