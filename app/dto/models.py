from pydantic import BaseModel, Field, ValidationError, validator
from typing import Optional
from decimal import Decimal
from app.utils.utils import formatar_data_str


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
    registro: int
    numero_inscricao_empresa: str
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


class ArquivoRetorno(BaseModel):
    header: HeaderArquivo
