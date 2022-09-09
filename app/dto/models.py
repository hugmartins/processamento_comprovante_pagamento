from pydantic import BaseModel, Field, validator
from typing import Optional, List
from utils.utils import formatar_data_str, formatar_valor_pagamento


class HeaderArquivo(BaseModel):
    banco: str
    lote: int
    tipo_registro: int
    numero_inscricao_empresa: str = Field(description="CNPJ da empresa")
    nome_empresa: str
    codigo_remessa_retorno: int = Field(description="Aceito apenas numero 2, quie significa arquivo retorno")
    data_geracao_arquivo_str: str
    hora_geracao_arquivo_str: str

    @validator('codigo_remessa_retorno')
    def validar_codigo_remessa_retorno(cls, v):
        if v != 2:
            raise ValueError('Arquivo bancario nao e arquivo de retorno pagamento!')
        return v

    @validator('data_geracao_arquivo_str')
    def formatar_data_geracao_arquivo(cls, v):
        return formatar_data_str(v, '%d%m%Y', '%d/%m/%Y')


class OcorrenciaPagamento(BaseModel):
    codigo_ocorrencia: str
    descricao_ocorrencia: str


class SegmentoA(BaseModel):
    tipo_registro: int
    codigo_segmento: str = Field(description="A ou B para retorno")
    codigo_banco_favorecido: str
    agencia: str
    digito_verificador_agencia: str
    numero_conta: str
    digito_verificador_conta: str
    digito_verificador_ag_conta: str
    nome_favorecido: str
    numero_documento: str
    data_pagamento_str: str
    valor_pagamento_str: str
    nosso_numero: str
    data_real_efetivacao_pagamento_str: str
    valor_real_efetivacao_pagamento_str: str
    ocorrencia: Optional[List[OcorrenciaPagamento]] = []

    @validator('data_pagamento_str')
    def formatar_data_geracao_arquivo(cls, v):
        return formatar_data_str(v, '%d%m%Y', '%d/%m/%Y')

    @validator('data_real_efetivacao_pagamento_str')
    def formatar_data_real_geracao_arquivo(cls, v):
        return formatar_data_str(v, '%d%m%Y', '%d/%m/%Y')

    @validator('valor_pagamento_str')
    def formatar_valor_pagamento(cls, v):
        return formatar_valor_pagamento(v, 13, 2)

    @validator('valor_real_efetivacao_pagamento_str')
    def formatar_valor_real_pagamento(cls, v):
        return formatar_valor_pagamento(v, 13, 2)


class SegmentoB(BaseModel):
    tipo_registro: int
    codigo_segmento: str = Field(description="A ou B para retorno")
    numero_inscricao_favorecido: str = Field(description="CPF ou CNPJ do favorecido")


class DetalheArquivo(BaseModel):
    segmento_a: Optional[SegmentoA] = None
    segmento_b: Optional[SegmentoB] = None


class TrailerLote(BaseModel):
    quantidade_registro: int
    tipo_registro: int
    total_pago_lote: str

    @validator('total_pago_lote')
    def formatar_valor_total_pago_lote(cls, v):
        return formatar_valor_pagamento(v, 16, 2)


class TrailerArquivo(BaseModel):
    quantidade_registro: int
    tipo_registro: int


class Lote(BaseModel):
    detalhe: List[DetalheArquivo]
    trailer_lote: TrailerLote


class ArquivoRetorno(BaseModel):
    header_arquivo: HeaderArquivo
    lote: Lote
    trailer_arquivo: TrailerArquivo


class ComprovantePagamentoFuncionario(BaseModel):
    nome_empresa_pagadora: str = Field(title="Nome empresa pagadora", default=None, example="CBM")
    data_geracao_arquivo_comprovante: str = Field(title="Data da geracao do arquivo de pagamento", default=None,
                                                  example="202208")
    detalhe_comprovante: DetalheArquivo = Field(title="Detalhe pagamentos", default=None)


class Funcionario(BaseModel):
    descricao_filial: str = Field(title="Descricao Filial", example="010001-ESCRITÓRIO CENTRAL")
    nome_completo: str = Field(title="Nome Funcionario", example="Fulano da Silva")
    id_funcionario: str = Field(title="Identificador Funcionario", example="0123456789", regex=r'^[0-9]{12}$')
    cpf: str = Field(title="CPF ou CNPJ Funcionario", example="12345678900", regex=r'(^[0-9]{11}$)|(^[0-9]{14}$)')
    agencia_salario: Optional[str] = None
    conta_salario: Optional[str] = None
    banco: str = Field(title="Banco Recebedor", example="BRADESCO")
    src_total_verba: str = Field(title="Valor Pagamento", example="1000,10")
    dados_comprovante: ComprovantePagamentoFuncionario = Field(title="Dados comprovante pagamento", default=None)


def gerar_novo_funcionario(funcionario: Funcionario):
    return Funcionario(
        descricao_filial=funcionario.descricao_filial,
        nome_completo=funcionario.nome_completo,
        id_funcionario=funcionario.id_funcionario,
        cpf=funcionario.cpf,
        agencia_salario=funcionario.agencia_salario,
        conta_salario=funcionario.conta_salario,
        banco=funcionario.banco,
        src_total_verba=funcionario.src_total_verba,
        dados_comprovante=funcionario.dados_comprovante
    )


class DetalheReportComprovante(BaseModel):
    nome_empresa_pagadora: str
    nome_favorecido: str
    cpf_favorecido: str
    agencia_pagamento: str
    conta_pagamento: str
    data_pagamento: str
    valor_pago: str
    numero_comprovante: str


class ReportComprovante(BaseModel):
    detalhe_report: List[DetalheReportComprovante]


class DetalheReportResultadoProcessamento(BaseModel):
    filial: str
    filial_sem_inconsistencias: bool
    nome_funcionario: Optional[str] = None
    cpf: Optional[str] = None
    valor_a_pagar: Optional[str] = None
    total_funcionarios: str
    total_com_comprovante: str
    total_sem_comprovante: str


class ReportResultadoProcessamento(BaseModel):
    detalhe_report: List[DetalheReportResultadoProcessamento]


class DetalheReportInconsistencias(BaseModel):
    filial: str
    nome_funcionario: str
    cpf: str
    valor_a_pagar: str
    codigo_ocorrencia: Optional[str] = None
    descricao_ocorrencia: Optional[str] = None
    total_inconsistencias: Optional[str] = None


class ReportInconsistencias(BaseModel):
    detalhe_report: List[DetalheReportInconsistencias]
