# PROCESSAMENTO COMPROVANTES PAGAMENTO

Geração de comprovantes de pagamento dos funcionarios relacionados no líquido folha de cada mês por meio dos retornos 
bancarios de pagamento.

## Bancos aceitos:
* BRADESCO

## Estrutura do Projeto

* app
  * dto 
    * models.py 
  * service 
    * arquivo_service.py
    * processamento_service.py 
    * relatorio_service.py 
  * utils 
    * exceptions.py
    * utils.py
  * iniciar_processamento.py 
* jasper_report
  * datasource
  * img
  * report 
* output
  * comprovantes
  * relatorio_processamento
  * relatorio_inconsistencias
* recursos
  * liquido_folha
  * previa_pagamento
  * retorno_bancario
* venv - interpretador python
* .gitignore
* README.md
* requirements.txt
* start_processamento.bat 

## Dependências
A aplicação foi desenvolvida utilizando da tecnologia Python 3.9, para o seu funcionamento, é necessario que na 
máquina tenha:
* Python 3.9 64 bits;
* Java JDK 8 64 bits ou 11 64 bits;
* acesso de leitura e escrita de arquivos nas pastas do projeto, tanto a aplicação quanto o usuario que irá executar 
a mesma;
* usuario com acesso para executar comandos no prompt de comando;

## Executando Projeto

### Recursos
Antes de executar a aplicação, é preciso preparar os recursos.

#### Liquido Folha
O líquido folha um arquivo do tipo **.csv** que deve ter as seguintes colunas: 

```csv
DESC FILIAL,NOMECOMPLETO,IDFUNCIONARIO,CPF,AGENCIASALARIO,CONTASALARIO,BANCOS,SRC-TOTAL VERBA L01
```
Os dados devem ser separdos por **;** (ponto e virgula), o arquivo deve ser salvo na pasta 
**recursos/liquido_folha**. A **aplicação não funciona com mais de um arquivo dentro da pasta**, sempre remova o anterior 
antes de adicionar o novo.

#### Arquivo de Retorno do Banco - PREVIA PAGAMENTO
Os arquivos de retorno da previa de pagamento, devem ser salvos na pasta **recurso/previa_pagamento** com a 
extensão **.ret**. Podem ser adicionados 
quantos arquivos forem necessarios para gerar o relatorio de inconsistencias.
Antes de salvar os retornos que serão utilizados, recomendamos a remoção de todos os arquivos bancarios (com 
as previas de outros meses), evitando a inconsistencia dos dados nos comprovantes gerados. 

#### Arquivo de Retorno do Banco - COMPROVANTES
Os arquivos de retorno de pagamentos (comprovantes), devem ser salvos na pasta **recurso/retorno_bancario** com a 
extensão **.ret**. Podem ser adicionados quantos arquivos forem necessarios para gerar os comprovantes.
Antes de salvar os retornos que serão utilizados, recomendamos a remoção de todos os arquivos bancarios (com 
pagamentos de outros meses), evitando a inconsistencia dos dados nos comprovantes gerados. 

### Como executar a aplicação
Na pasta do projeto tem o arquivo **start_processamento.bat**, onde deve ser aberto com duplo click do mouse. Esse 
arquivo irá abrir o prompt de comando e então será dada duas opções para seguir com o processamento. Para 
processamento da previa de pagamento, selecionar a opção 1, para o processamento dos comprovantes, selecionar a 
opção 2, conforme aparecer na tela.
As etapas serão 
exibidas na 
tela em forma de logs, é importante acompanhar as mensagens exibidas para saber em qual etapa do processamento a 
aplicação está.
Em caso de erro no processamento, solicitamos que tire uma fotografia (print) da tela de execução para melhor 
análise do problema.

### Resultado processamento - PREVIA PAGAMENTO
Ao término do processamento, será gerado um relatorio para cada filial que tenha inconsistencias na pasta 
**output/relatorio_inconsistencias**.

### Resultado processamento - COMPROVANTES
Ao término do processamento, os comprovantes estarão salvos na pasta **output/comprovantes** separados por filial.
É gerado tambem o relatorio de **Resultado do Processamento**, localizado na pasta 
**output/relatorio_processamento**, onde é informado a quantidade de comprovantes gerados e os funcionarios com 
inconsistencia (sem comprovante), com base no arquivo líquido folha.
