import logging
from typing import List
from app.utils.exceptions import finalizar_programa_error
from app.utils.utils import formatar_data_str
from app.dto.models import Funcionario, ArquivoRetorno, ComprovantePagamentoFuncionario, gerar_novo_funcionario
from app.dto.enums import TipoArquivoProcessamento
from app.service.arquivo_service import ArquivoService
from app.service.relatorio_service import RelatorioService
from app.dto.constant import INCREMENTE_MAIS_UM


class ProcessamentoService:
    def __init__(self):
        self.opcao_processamento = None
        self.map_total_funcionarios_por_filial = {}
        self.map_funcionarios_com_comprovante_por_filial = {}
        self.map_funcionarios_sem_comprovante_por_filial = {}
        self.map_funcionarios_inconsistentes_por_filial = {}

        self.total_funcionarios_com_comprovante = 0
        self.total_funcionarios_sem_comprovante = 0

        self.arquivo_service = ArquivoService()

    def iniciar_processamento(self, opcao_processamento=int):
        self.opcao_processamento = opcao_processamento

        funcionarios_liquido_folha = self.arquivo_service.carregar_lista_funcionarios_liquido_folha()

        if len(funcionarios_liquido_folha) > 0:
            logging.info(f'Liquido Folha com sucesso! Total funcionarios: {len(funcionarios_liquido_folha)}')
        else:
            finalizar_programa_error('Nenhum dado encontrado no Liquido Folha, favor verificar!')

        self.__switch_processamento(funcionarios_liquido_folha)

    def __switch_processamento(self, funcionarios_liquido_folha: List[Funcionario]):
        if self.opcao_processamento == TipoArquivoProcessamento.COMPROVANTE_PAGAMENTO.value:
            self.__processar_comprovante_pagamento(funcionarios_liquido_folha)
        elif self.opcao_processamento == TipoArquivoProcessamento.PREVIA_PAGAMENTO.value:
            self.__processar_previa_pagamento(funcionarios_liquido_folha)

    def __processar_previa_pagamento(self, funcionarios_liquido_folha: List[Funcionario]):
        lista_arquivos_previa_pagamento = \
            self.arquivo_service.carregar_retornos_bancario(TipoArquivoProcessamento.PREVIA_PAGAMENTO)

        if len(lista_arquivos_previa_pagamento) > 0:
            logging.info(f'Retornos previa pagamentos carregados com sucesso! '
                         f'Total arquivos de retorno: {len(lista_arquivos_previa_pagamento)}')
        else:
            finalizar_programa_error('Nenhum dado encontrado no retorno previa pagamento, favor verificar!')

        self.__buscar_inconsistencia_pagamento_funcionario(funcionarios_liquido_folha, lista_arquivos_previa_pagamento)

        if len(self.map_funcionarios_inconsistentes_por_filial) == 0:
            finalizar_programa_error('Nao foram encontrados funcionarios com inconsistencia no pagamento!')
        else:
            RelatorioService().gerar_relatorio_inconsistencias(self.map_funcionarios_inconsistentes_por_filial)

    def __processar_comprovante_pagamento(self, funcionarios_liquido_folha: List[Funcionario]):
        lista_arquivos_retorno_bancario = \
            self.arquivo_service.carregar_retornos_bancario(TipoArquivoProcessamento.COMPROVANTE_PAGAMENTO)

        if len(lista_arquivos_retorno_bancario) > 0:
            logging.info(f'Retornos comprovante pagamento carregados com sucesso! '
                         f'Total arquivos de retorno: {len(lista_arquivos_retorno_bancario)}')
        else:
            finalizar_programa_error('Nenhum dado encontrado no retorno comprovante pagamento, favor verificar!')

        self.__burcar_comprovante_funcionario(funcionarios_liquido_folha, lista_arquivos_retorno_bancario)

        logging.info(f'funcionarios COM comprovante: {self.total_funcionarios_com_comprovante}')
        logging.warning(f'funcionarios SEM comprovante: {self.total_funcionarios_sem_comprovante}')

        relatorio_service = RelatorioService()

        relatorio_service.gerar_relatorio_comprovante(self.map_funcionarios_com_comprovante_por_filial)

        map_quantidade_comprovantes_por_filial = self.__transformar_map_funcionarios_com_comprovante_por_filial()
        relatorio_service.gerar_relatorio_resultado_processamento(self.map_total_funcionarios_por_filial,
                                                                  map_quantidade_comprovantes_por_filial,
                                                                  self.map_funcionarios_sem_comprovante_por_filial)

    def __transformar_map_funcionarios_com_comprovante_por_filial(self) -> dict:
        map_quantidade_comprovantes_por_filial = {}
        for codigo_filial in self.map_funcionarios_com_comprovante_por_filial:
            lista_funcionarios = self.map_funcionarios_com_comprovante_por_filial[codigo_filial]
            map_quantidade_comprovantes_por_filial[codigo_filial] = len(lista_funcionarios)

        return map_quantidade_comprovantes_por_filial

    def __burcar_comprovante_funcionario(self, funcionarios_liquido_folha: List[Funcionario],
                                         lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
        for funcionario in funcionarios_liquido_folha:
            comprovante_encontrado = False
            self.__contabilizar_quantidade_funcionarios_por_filial(funcionario.descricao_filial)
            for arquivo_retorno in lista_arquivos_retorno_bancario:
                for detalhe in arquivo_retorno.lote.detalhe:
                    if funcionario.cpf in detalhe.segmento_b.numero_inscricao_favorecido:
                        comprovante_encontrado = True

                        data_geracao_arquivo = formatar_data_str(
                            data_str=arquivo_retorno.header_arquivo.data_geracao_arquivo_str,
                            formato_entrada='%d/%m/%Y',
                            formato_saida='%Y%m'
                        )

                        funcionario.dados_comprovante = ComprovantePagamentoFuncionario(
                            nome_empresa_pagadora=arquivo_retorno.header_arquivo.nome_empresa,
                            data_geracao_arquivo_comprovante=data_geracao_arquivo,
                            detalhe_comprovante=detalhe
                        )

                        funcionario_com_comprovante = gerar_novo_funcionario(funcionario)
                        self.__adicionar_funcionario_lista_funcionario_comprovante_por_filial(
                            funcionario_com_comprovante
                        )

            if comprovante_encontrado is False:
                self.__adicionar_funcionario_lista_funcionario_sem_comprovante_por_filial(funcionario)

    def __buscar_inconsistencia_pagamento_funcionario(self, funcionarios_liquido_folha: List[Funcionario],
                                                      lista_arquivos_retorno_bancario: List[ArquivoRetorno]):
        for funcionario in funcionarios_liquido_folha:
            for arquivo_retorno in lista_arquivos_retorno_bancario:
                for detalhe in arquivo_retorno.lote.detalhe:
                    if funcionario.cpf in detalhe.segmento_b.numero_inscricao_favorecido:
                        data_geracao_arquivo = formatar_data_str(
                            data_str=arquivo_retorno.header_arquivo.data_geracao_arquivo_str,
                            formato_entrada='%d/%m/%Y',
                            formato_saida='%Y%m'
                        )

                        funcionario.dados_comprovante = ComprovantePagamentoFuncionario(
                            nome_empresa_pagadora=arquivo_retorno.header_arquivo.nome_empresa,
                            data_geracao_arquivo_comprovante=data_geracao_arquivo,
                            detalhe_comprovante=detalhe
                        )
                        self.__adicionar_funcionario_lista_inconsistencias_pagamento_por_filial(funcionario)

    def __adicionar_funcionario_lista_funcionario_comprovante_por_filial(self, funcionario: Funcionario):
        codigo_filial = funcionario.descricao_filial.split("-")[0]

        if codigo_filial in self.map_funcionarios_com_comprovante_por_filial:
            lista_funcionarios_filial = self.map_funcionarios_com_comprovante_por_filial[codigo_filial]
            lista_funcionarios_filial.append(funcionario)
            self.map_funcionarios_com_comprovante_por_filial[codigo_filial] = lista_funcionarios_filial
        else:
            self.map_funcionarios_com_comprovante_por_filial[codigo_filial] = [funcionario]
        self.total_funcionarios_com_comprovante += 1

    def __adicionar_funcionario_lista_funcionario_sem_comprovante_por_filial(self, funcionario: Funcionario):
        codigo_filial = funcionario.descricao_filial.split("-")[0]

        if codigo_filial in self.map_funcionarios_sem_comprovante_por_filial:
            lista_funcionarios_filial = self.map_funcionarios_sem_comprovante_por_filial[codigo_filial]
            lista_funcionarios_filial.append(funcionario)
            self.map_funcionarios_sem_comprovante_por_filial[codigo_filial] = lista_funcionarios_filial
        else:
            self.map_funcionarios_sem_comprovante_por_filial[codigo_filial] = [funcionario]
        self.total_funcionarios_sem_comprovante += 1

    def __contabilizar_quantidade_funcionarios_por_filial(self, nome_filial: str):
        codigo_filial = nome_filial.split("-")[0]
        if codigo_filial in self.map_total_funcionarios_por_filial:
            quantidade_funcionarios_filial = int(
                self.map_total_funcionarios_por_filial[codigo_filial]["quantidade_funcionario"])
            self.map_total_funcionarios_por_filial[codigo_filial]["quantidade_funcionario"] = \
                quantidade_funcionarios_filial + INCREMENTE_MAIS_UM
        else:
            self.map_total_funcionarios_por_filial[codigo_filial] = {
                "nome_filial": nome_filial, "quantidade_funcionario": INCREMENTE_MAIS_UM
            }

    def __adicionar_funcionario_lista_inconsistencias_pagamento_por_filial(self, funcionario: Funcionario):
        codigo_filial = funcionario.descricao_filial.split("-")[0]

        if codigo_filial in self.map_funcionarios_inconsistentes_por_filial:
            lista_funcionarios_filial = self.map_funcionarios_inconsistentes_por_filial[codigo_filial]
            lista_funcionarios_filial.append(funcionario)
            self.map_funcionarios_inconsistentes_por_filial[codigo_filial] = lista_funcionarios_filial
        else:
            self.map_funcionarios_inconsistentes_por_filial[codigo_filial] = [funcionario]
