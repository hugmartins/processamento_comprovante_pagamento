import os
import logging
from typing import List
from app.dto.models import Funcionario, ReportComprovante, DetalheReportComprovante, ResumoFilial
from pyreportjasper import PyReportJasper
from app.utils.utils import data_atual_formatada, formatar_cpf_funcionario
from app.utils.exceptions import finalizar_programa_error
from app.service.arquivo_service import criar_arquivo_datasource


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

        criar_arquivo_datasource(nome_arquivo_datasource, comprovante_report)
        montar_parametros_para_gerar_relatorio_comprovante_pagamento(codigo_filial, data_geracao_arquivo_pagamento,
                                                                     nome_arquivo_datasource)


def gerar_relatorio_resultado_processamento(resumo_filiais: List[ResumoFilial],
                                            map_dados_funcionarios_sem_comprovante: dict):
    print(resumo_filiais)
    print(map_dados_funcionarios_sem_comprovante)
    logging.info("Gerando relatorio com resultado do processamento")


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
        conn = {
            'driver': 'csv',
            'data_file': os.path.abspath(os.path.join(RESOURCES_DIR, f'{nome_datasource}.csv')),
            'csv_charset': 'utf-8',
            'csv_out_charset': 'utf-8',
            'csv_field_del': ',',
            'csv_out_field_del': ',',
            'csv_record_del': "\n",
            'csv_first_row': True,
            'csv_columns': list(DetalheReportComprovante.schema()["properties"].keys())
        }

        gerar_relatorio_jaspersoft(input_file, output_file, conn)

        logging.info(f'Comprovantes da filial {codigo_filial} gerados com sucesso. {output_file}.pdf')
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar PDF a partir do datasource {nome_datasource}. {error}')


def montar_parametros_para_gerar_relatorio_resultado_processamento(codigo_filial: str, nome_datasource: str):
    try:
        input_file = os.path.join(REPORTS_DIR, 'relatorio_processamento_comprovante.jrxml')
        output_file = os.path.join(DIR_RELATORIO_RESULTADO_PROCESSAMENTO
                                   , f'RESULTADO_PROCESSAMENTO_{data_atual_formatada("%d_%m_%Y_%H%M%S")}')
        conn = {
            'driver': 'csv',
            'data_file': os.path.abspath(os.path.join(RESOURCES_DIR, f'{nome_datasource}.csv')),
            'csv_charset': 'utf-8',
            'csv_out_charset': 'utf-8',
            'csv_field_del': ',',
            'csv_out_field_del': ',',
            'csv_record_del': "\n",
            'csv_first_row': True,
            'csv_columns': list(DetalheReportComprovante.schema()["properties"].keys())
        }

        gerar_relatorio_jaspersoft(input_file, output_file, conn)

        logging.info(f'Relatorio com resultado do processamento gerado com sucesso. {output_file}.pdf')
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar PDF a partir do datasource {nome_datasource}. {error}')


def gerar_relatorio_jaspersoft(input_file: str, output_file: str, conn: dict):
    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
        input_file,
        output_file,
        output_formats=["pdf"],
        db_connection=conn
    )
    pyreportjasper.process_report()
