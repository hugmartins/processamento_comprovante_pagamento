from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
    carregar_lista_funcionarios_liquido_folha, carregar_retornos_bancario


def iniciar_processamento():
    validar_arquivos_existentes()
    # lista_funcionarios_liquido_folha = carregar_lista_funcionarios_liquido_folha()
    lista_arquivos_retorno_bancario = carregar_retornos_bancario()


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()
