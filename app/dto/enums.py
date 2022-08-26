from enum import Enum


class TipoArquivoProcessamento(Enum):
    PREVIA_PAGAMENTO = 1
    COMPROVANTE_PAGAMENTO = 2


class OpcaoProcessamento(Enum):
    OP_UM = {"num_op": 1, "texto": "1 - Processar previa pagamento"}
    OP_DOIS = {"num_op": 2, "texto": "2 - Processar comprovante pagamento"}


class TipoRegistro(Enum):
    HEADER_ARQUIVO = 0, "Header de Arquivo"
    HEADER_LOTE = 1, "Header de Lote"
    REGIS_INIC_LOTE = 2, "Registros Iniciais do Lote"
    DETALHE = 3, "Detalhe"
    REGIS_FINAL_LOTE = 4, "Registros Finais do Lote"
    TRAILER_LOTE = 5, "Trailer de Lote"
    TRAILER_ARQUIVO = 9, "Trailer de Arquivo"
