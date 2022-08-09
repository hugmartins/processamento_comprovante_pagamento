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
    logging.info(f'Iniciando processamento comprovantes bancarios: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    iniciar_processamento()
    logging.info(f'Processamento comprovantes finalizado: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
