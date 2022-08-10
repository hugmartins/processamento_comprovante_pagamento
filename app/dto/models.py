from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class Funcionario(BaseModel):
    nome_completo: str = Field(title="Nome Funcionario", example="Fulano da Silva")
    id_funcionario: str = Field(title="Identificador Funcionario", example="0123456789", regex=r'^[0-9]{12}$')
    cpf: str = Field(title="CPF Funcionario", example="12345678900", regex=r'(^[0-9]{11}$)|(^[0-9]{14}$)')
    agencia_salario: Optional[str] = None
    conta_salario: Optional[str] = None
    banco: str = Field(title="Banco Recebedor", example="BRADESCO")
    src_total_verba: Decimal = Field(title="Valor Pagamento", example="1.000,10")


class Filial(BaseModel):
    descricao_filial: str = Field(title="Descricao Filial", example="010001-ESCRITÓRIO CENTRAL")
    funcionarios: List[Funcionario] = []
