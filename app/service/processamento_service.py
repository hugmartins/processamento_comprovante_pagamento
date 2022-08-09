from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario


def iniciar_processamento():
    validar_arquivos_existentes()


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()