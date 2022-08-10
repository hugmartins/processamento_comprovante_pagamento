import csv
from decimal import Decimal
from app.service.arquivo_service import validar_diretorio_liquido_folha, validar_diretorio_retorno_bancario, \
                                        carregar_endereco_arquivo_liquido_folha
from app.dto.models import Funcionario, Filial


MAP_LIQUIDO_FOLHA = {}


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
            funcionario = Funcionario(
                nome_completo=linha[1],
                id_funcionario=linha[2],
                cpf=linha[3],
                agencia_salario=linha[4],
                conta_salario=linha[5],
                banco=linha[6],
                src_total_verba=Decimal(linha[7].replace(".", "").replace(",", "."))
            )

            filial = Filial(descricao_filial=linha[0])
            filial.funcionarios.append(funcionario)

            print(filial.descricao_filial)
            print(filial.funcionarios[0].nome_completo)
            print(filial.funcionarios[0].src_total_verba)
            break


def validar_arquivos_existentes():
    validar_diretorio_liquido_folha()
    validar_diretorio_retorno_bancario()
