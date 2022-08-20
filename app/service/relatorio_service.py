import os
import logging
from app.dto.models import Funcionario, ReportComprovante, DetalheReportComprovante
from pyreportjasper import PyReportJasper
from app.utils.utils import data_atual_formatada, formatar_cpf_funcionario
from app.utils.exceptions import finalizar_programa_error
from app.service.arquivo_service import criar_arquivo_datasource


RESOURCES_DIR = '../jasper_report/datasource/'
REPORTS_DIR = '../jasper_report/report/'


def gerar_relatorio_comprovante(map_funcionarios_comprovante: dict):
    for codigo_filial in map_funcionarios_comprovante:
        logging.info(f'Gerando comprovantes da filial {codigo_filial}.')
        lista_report_comprovante = []
        for funcionario_filial in map_funcionarios_comprovante[codigo_filial]:
            detalhe_comprovante_report = converter_funcionario_para_report_comprovante(funcionario_filial)
            lista_report_comprovante.append(detalhe_comprovante_report)

        comprovante_report = ReportComprovante(detalhe_report=lista_report_comprovante)
        data_nome_arquivo = data_atual_formatada()
        nome_arquivo = f'{codigo_filial}_comprovantes_pagamento_{data_nome_arquivo}'

        criar_arquivo_datasource(nome_arquivo, comprovante_report)


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

    return DetalheReportComprovante(
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


def json_to_pdf(nome_datasource: str):
    try:
        input_file = os.path.join(REPORTS_DIR, 'comprovante_pagamento_bradesco.jrxml')
        output_file = os.path.join(REPORTS_DIR, 'comprovante_pagamento_bradesco')
        conn = {
            'driver': 'json',
            'data_file': os.path.join(RESOURCES_DIR, f'{nome_datasource}.json'),
            'json_query': 'detalhe_report'
        }
        pyreportjasper = PyReportJasper()
        pyreportjasper.config(
            input_file,
            output_file,
            output_formats=["pdf"],
            db_connection=conn
        )
        pyreportjasper.process_report()
        print('Result is the file below.')
        print(output_file + '.pdf')
    except Exception as error:
        finalizar_programa_error(f'Erro ao tentar gerar PDF a partir do datasource {nome_datasource}. {error}')
