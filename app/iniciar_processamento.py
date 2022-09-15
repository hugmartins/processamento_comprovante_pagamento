import logging
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.service.processamento_service import iniciar_processamento
from app.dto.enums import OpcaoProcessamento
from app.service.arquivo_service import excluir_datasources_existentes


def configurar_log():
    config_log_file = RotatingFileHandler(
        filename='log_processamento.log',
        mode='a',
        maxBytes=5 * 1024 * 1024,
        backupCount=1
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            config_log_file,
            logging.StreamHandler()
        ],
    )


def executar_configuracoes_iniciais():
    configurar_log()
    excluir_datasources_existentes()


def iniciar():
    executar_configuracoes_iniciais()
    print(OpcaoProcessamento.OP_UM.value["texto"])
    print(OpcaoProcessamento.OP_DOIS.value["texto"])
    opcao = input('Opcao: ')

    validar_opcao_selecionada(opcao)


def validar_opcao_selecionada(opcao_selecionada: str):
    lista_opcoes_aceitas = [opcao.value['num_op'] for opcao in OpcaoProcessamento]

    if not opcao_selecionada.isdigit() or int(opcao_selecionada) not in lista_opcoes_aceitas:
        logging.error(f'Opcao "{opcao_selecionada}" invalida. \n\n')
        time.sleep(1)
        iniciar()
    else:
        processar_opcao_usuario(int(opcao_selecionada))


def processar_opcao_usuario(opcao_selecionada: int):

    data_hora_inicio_execucao = datetime.now()
    logging.info(f'Iniciando processamento comprovantes bancarios: {data_hora_inicio_execucao.strftime("%d/%m/%Y %H:%M:%S")}.')
    iniciar_processamento(opcao_selecionada)
    data_hora_fim_execucao = datetime.now()
    logging.info(f'Processamento comprovantes finalizado: {data_hora_fim_execucao.strftime("%d/%m/%Y %H:%M:%S")}.')

    durancao_processamento = data_hora_fim_execucao - data_hora_inicio_execucao
    logging.info(f'Duração processamento: {durancao_processamento}')


iniciar()

