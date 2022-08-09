import csv
from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
                                        carregar_endereco_arquivo_liquido_folha


def iniciar_processamento():
    validar_arquivos_existentes()
    arq_liquido_folha = carregar_endereco_arquivo_liquido_folha()
    buscar_comprovante_por_funcionario(arq_liquido_folha)


def buscar_comprovante_por_funcionario(arq_liquido_folha: str):
    with open(arq_liquido_folha, 'r') as arquivo:
        dados_liquido_folha = csv.reader(arquivo, delimiter=';')

        # pular cabeçalho
        next(dados_liquido_folha, None)
        for linha in dados_liquido_folha:
            print(linha)
            print(linha[0])
            print(linha[1])
            print(linha[2])
            print(linha[3])
            print(linha[4])
            print(linha[5])
            print(linha[6])
            print(linha[7])
            break


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()
