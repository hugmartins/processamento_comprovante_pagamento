from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from enum import Enum
from app.utils.utils import formatar_data_str, formatar_valor_pagamento


class TipoRegistro(Enum):
    HEADER_ARQUIVO = 0, "Header de Arquivo"
    HEADER_LOTE = 1, "Header de Lote"
    REGIS_INIC_LOTE = 2, "Registros Iniciais do Lote"
    DETALHE = 3, "Detalhe"
    REGIS_FINAL_LOTE = 4, "Registros Finais do Lote"
    TRAILER_LOTE = 5, "Trailer de Lote"
    TRAILER_ARQUIVO = 9, "Trailer de Arquivo"


class Funcionario(BaseModel):
    descricao_filial: str = Field(title="Descricao Filial", example="010001-ESCRITÓRIO CENTRAL")
    nome_completo: str = Field(title="Nome Funcionario", example="Fulano da Silva")
    id_funcionario: str = Field(title="Identificador Funcionario", example="0123456789", regex=r'^[0-9]{12}$')
    cpf: str = Field(title="CPF Funcionario", example="12345678900", regex=r'(^[0-9]{11}$)|(^[0-9]{14}$)')
    agencia_salario: Optional[str] = None
    conta_salario: Optional[str] = None
    banco: str = Field(title="Banco Recebedor", example="BRADESCO")
    src_total_verba: Decimal = Field(title="Valor Pagamento", example="1.000,10")


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

    @validator('data_pagamento_str')
    def formatar_data_geracao_arquivo(cls, v):
        return formatar_data_str(v, '%d%m%Y', '%d/%m/%Y')

    @validator('data_real_efetivacao_pagamento_str')
    def formatar_data_real_geracao_arquivo(cls, v):
        return formatar_data_str(v, '%d%m%Y', '%d/%m/%Y')

    @validator('valor_pagamento_str')
    def formatar_valor_pagamento(cls, v):
        return formatar_valor_pagamento(v)

    @validator('valor_real_efetivacao_pagamento_str')
    def formatar_valor_real_pagamento(cls, v):
        return formatar_valor_pagamento(v)


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
        return formatar_valor_pagamento(v)


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
