import os
import logging
from pyreportjasper import PyReportJasper

from dto.models import Funcionario, ReportComprovante, DetalheReportComprovante, ReportResultadoProcessamento, \
    DetalheReportResusltadoProcessamento
from utils.utils import data_atual_formatada, formatar_cpf_funcionario
from utils.exceptions import finalizar_programa_error
from service.arquivo_service import criar_arquivo_datasource_comprovante_pagamento, \
    criar_arquivo_datasource_resultado_processamento

RESOURCES_DIR = '../jasper_report/datasource/'
REPORTS_DIR = '../jasper_report/report/'
DIR_COMPROVANTE_POR_FILIAL = '../resources/saida/comprovantes/'
DIR_RELATORIO_RESULTADO_PROCESSAMENTO = '../resources/saida/relatorio_processamento/'
DIR_IMG_REPORT = '../jasper_report/img/'


def gerar_relatorio_comprovante(map_funcionarios_comprovante: dict):
    for codigo_filial in map_funcionarios_comprovante:
        logging.info(f'Gerando comprovantes da filial {codigo_filial}.')

        lista_report_comprovante = []
        data_geracao_arquivo_pagamento = None

        for funcionario_filial in map_funcionarios_comprovante[codigo_filial]:
            data_geracao_arquivo_pagamento = funcionario_filial.dados_comprovante.data_geracao_arquivo_comprovante
            detalhe_comprovante_report = converter_funcionario_para_report_comprovante(funcionario_filial)
            lista_report_comprovante.append(detalhe_comprovante_report)

        comprovante_report = ReportComprovante(detalhe_report=lista_report_comprovante)
        data_nome_arquivo = data_atual_formatada()
        nome_arquivo_datasource = f'{codigo_filial}_comprovantes_pagamento_{data_nome_arquivo}'

        criar_arquivo_datasource_comprovante_pagamento(nome_arquivo_datasource, comprovante_report)
        montar_parametros_para_gerar_relatorio_comprovante_pagamento(codigo_filial, data_geracao_arquivo_pagamento,
                                                                     nome_arquivo_datasource)


def gerar_relatorio_resultado_processamento(total_funcionarios_por_filial: dict,
                                            dados_funcionarios_com_comprovante_por_filial: dict,
                                            dados_funcionarios_sem_comprovante_por_filial: dict):
    logging.info("Gerando relatorio com resultado do processamento")
    relatorio_resultado_processamento = \
        criar_report_resultado_processamento(total_funcionarios_por_filial,
                                             dados_funcionarios_com_comprovante_por_filial,
                                             dados_funcionarios_sem_comprovante_por_filial)

    nome_datasource_resultado_processamento = f'DATASOURCE_RESULTADO_PROCESSAMENTO_{data_atual_formatada()}'
    criar_arquivo_datasource_resultado_processamento(nome_datasource_resultado_processamento,
                                                     relatorio_resultado_processamento)
    montar_parametros_para_gerar_relatorio_resultado_processamento(nome_datasource_resultado_processamento)


def criar_report_resultado_processamento(total_funcionarios_por_filial: dict,
                                         dados_funcionarios_com_comprovante_por_filial: dict,
                                         dados_funcionarios_sem_comprovante_por_filial: dict) -> ReportResultadoProcessamento:
    lista_resultado_processamento = []
    for codigo_filial in total_funcionarios_por_filial:
        lista_funcionarios_sem_comprovante = []
        total_funcionario_com_comprovante = 0
        total_funcionario_sem_comprovante = 0

        if codigo_filial in dados_funcionarios_com_comprovante_por_filial:
            total_funcionario_com_comprovante = dados_funcionarios_com_comprovante_por_filial[codigo_filial]

        if codigo_filial in dados_funcionarios_sem_comprovante_por_filial:
            total_funcionario_sem_comprovante = len(dados_funcionarios_sem_comprovante_por_filial[codigo_filial])
            lista_funcionarios_sem_comprovante = dados_funcionarios_sem_comprovante_por_filial[codigo_filial]

        filial = total_funcionarios_por_filial[codigo_filial]
        nome_filial = filial['nome_filial']
        quantidade_funcionarios_filial = filial['quantidade_funcionario']

        if len(lista_funcionarios_sem_comprovante) > 0:
            for funcionario in lista_funcionarios_sem_comprovante:
                cpf = formatar_cpf_funcionario(funcionario.cpf)
                resultado_processamento_funcionario = gerar_detalhe_report_resultado_processamento(
                    nome_filial, quantidade_funcionarios_filial, total_funcionario_com_comprovante,
                    total_funcionario_sem_comprovante, funcionario.nome_completo, cpf, funcionario.src_total_verba
                )

                lista_resultado_processamento.append(resultado_processamento_funcionario)
        else:
            resultado_processamento_filial = gerar_detalhe_report_resultado_processamento(
                nome_filial, quantidade_funcionarios_filial, total_funcionario_com_comprovante,
                total_funcionario_sem_comprovante
            )
            lista_resultado_processamento.append(resultado_processamento_filial)

    return ReportResultadoProcessamento(detalhe_report=lista_resultado_processamento)


def gerar_detalhe_report_resultado_processamento(nome_filial: str,
                                                 total_funcionarios_filial: int,
                                                 total_funcionarios_com_comprovante: int,
                                                 total_funcionarios_sem_comprovante: int, nome_funcionario: str = None,
                                                 cpf: str = None,
                                                 valor_a_pagar: str = None) -> DetalheReportResusltadoProcessamento:
    return DetalheReportResusltadoProcessamento(
        data_atual=data_atual_formatada('%d/%m/%Y'),
        logo_cbm=os.path.abspath(os.path.join(DIR_IMG_REPORT, 'logo_cbm.png')),
        filial=nome_filial,
        nome_funcionario=nome_funcionario,
        cpf=cpf,
        valor_a_pagar=valor_a_pagar,
        total_funcionarios=total_funcionarios_filial,
        total_com_comprovante=total_funcionarios_com_comprovante,
        total_sem_comprovante=total_funcionarios_sem_comprovante
    )


def converter_funcionario_para_report_comprovante(funcionario: Funcionario) -> DetalheReportComprovante:
    cpf = formatar_cpf_funcionario(funcionario.cpf)
    agencia_pagamento = gerar_agencia_ou_conta_com_digito_verificador(
        funcionario.dados_comprovante.detalhe_comprovante.segmento_a.agencia,
        int(funcionario.dados_comprovante.detalhe_comprovante.segmento_a.digito_verificador_agencia)
    )
    conta_pagamento = gerar_agencia_ou_conta_com_digito_verificador(
        funcionario.dados_comprovante.detalhe_comprovante.segmento_a.numero_conta,
        int(funcionario.dados_comprovante.detalhe_comprovante.segmento_a.digito_verificador_conta)
    )

    diretorio_completo_logo_bradesco = os.path.abspath(os.path.join(DIR_IMG_REPORT, 'logo_bradesco.png'))

    return DetalheReportComprovante(
        logo_bradesco=diretorio_completo_logo_bradesco,
        data_emissao_relatorio=data_atual_formatada('%d/%m/%Y'),
        nome_empresa_pagadora=funcionario.dados_comprovante.nome_empresa_pagadora.upper(),
        nome_favorecido=funcionario.nome_completo.upper(),
        cpf_favorecido=cpf,
        agencia_pagamento=agencia_pagamento,
        valor_pago=funcionario.dados_comprovante.detalhe_comprovante.segmento_a.valor_pagamento_str,
        numero_comprovante=funcionario.dados_comprovante.detalhe_comprovante.segmento_a.nosso_numero,
        data_pagamento=funcionario.dados_comprovante.detalhe_comprovante.segmento_a.data_pagamento_str,
        conta_pagamento=conta_pagamento
    )


def gerar_agencia_ou_conta_com_digito_verificador(agencia_ou_conta: str, digito_verificador: int) -> str:
    if digito_verificador is None:
        digito_verificador = 0

    return ''.join((agencia_ou_conta, '-', str(digito_verificador)))


def montar_parametros_para_gerar_relatorio_comprovante_pagamento(codigo_filial: str, data_geracao_arquivo: str,
                                                                 nome_datasource: str):
    try:
        input_file = os.path.join(REPORTS_DIR, 'comprovante_pagamento_bradesco.jrxml')
        output_file = os.path.join(DIR_COMPROVANTE_POR_FILIAL
                                   , f'{codigo_filial} - {data_geracao_arquivo} - COMPROVANTES FOLPAG BRADESCO')
        nome_colunas_csv = list(DetalheReportComprovante.schema()["properties"].keys())

        gerar_relatorio_jaspersoft(input_file, output_file, nome_datasource, nome_colunas_csv)

        logging.info(f'Comprovantes da filial {codigo_filial} gerados com sucesso. {output_file}.pdf')
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar PDF a partir do datasource {nome_datasource}. {error}')


def montar_parametros_para_gerar_relatorio_resultado_processamento(nome_datasource: str):
    try:
        input_file = os.path.join(REPORTS_DIR, 'relatorio_processamento_comprovante.jrxml')
        output_file = os.path.join(DIR_RELATORIO_RESULTADO_PROCESSAMENTO
                                   , f'RESULTADO_PROCESSAMENTO_{data_atual_formatada("%d_%m_%Y_%H%M%S")}')
        nome_colunas_csv = list(DetalheReportResusltadoProcessamento.schema()["properties"].keys())

        gerar_relatorio_jaspersoft(input_file, output_file, nome_datasource, nome_colunas_csv)

        logging.info(f'Relatorio com resultado do processamento gerado com sucesso. {output_file}.pdf')
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar PDF a partir do datasource {nome_datasource}. {error}')


def gerar_relatorio_jaspersoft(input_file: str, output_file: str, nome_datasource: str, nome_colunas_csv: list):

    conn = {
        'driver': 'csv',
        'data_file': os.path.abspath(os.path.join(RESOURCES_DIR, f'{nome_datasource}.csv')),
        'csv_charset': 'utf-8',
        'csv_out_charset': 'utf-8',
        'csv_field_del': ',',
        'csv_out_field_del': ',',
        'csv_record_del': "\n",
        'csv_first_row': True,
        'csv_columns': nome_colunas_csv
    }

    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
        input_file,
        output_file,
        output_formats=["pdf"],
        db_connection=conn
    )
    pyreportjasper.process_report()
