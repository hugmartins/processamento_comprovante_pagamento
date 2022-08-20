import os
from typing import List
from app.dto.models import Funcionario, ReportComprovante
from pyreportjasper import PyReportJasper


def gerar_relatorio_comprovante(map_funcionarios_comprovante: dict):
    print('gerando_relatorio')


def preparar_objeto_para_gerar_relatorio(funcionarios: Funcionario) -> List[ReportComprovante]:
    return [ReportComprovante()]


def json_to_pdf():
    RESOURCES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources')
    REPORTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'reports')
    input_file = os.path.join(REPORTS_DIR, 'json.jrxml')
    output_file = os.path.join(REPORTS_DIR, 'json')
    conn = {
        'driver': 'json',
        'data_file': os.path.join(self.RESOURCES_DIR, 'contacts.json'),
        'json_query': 'contacts.person'
    }
    pyreportjasper = PyReportJasper()
    self.pyreportjasper.config(
        input_file,
        output_file,
        output_formats=["pdf"],
        db_connection=conn
    )
    self.pyreportjasper.process_report()
    print('Result is the file below.')
    print(output_file + '.pdf')
