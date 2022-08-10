from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class LinhaLiquidoFolha(BaseModel):
    descricao_filial: str
    nome_completo: str
    id_funcionario: str
    cpf: str
    agencia_salario: Optional[str]
    conta_salario: Optional[str]
    banco: str
    src_total_verba: Decimal
