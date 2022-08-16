import logging
from datetime import datetime
from app.service.processamento_service import iniciar_processamento


def configurar_log():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


if __name__ == '__main__':
    configurar_log()

    data_inicio_execucao = datetime.now()
    logging.info(f'Iniciando processamento comprovantes bancarios: {data_inicio_execucao.strftime("%d/%m/%Y %H:%M:%S")}.')
    iniciar_processamento()
    data_fim_execucao = datetime.now()
    logging.info(f'Processamento comprovantes finalizado: {data_fim_execucao.strftime("%d/%m/%Y %H:%M:%S")}.')

    durancao_processamento = data_fim_execucao - data_inicio_execucao
    logging.info(f'Duração processamento: {durancao_processamento}')
