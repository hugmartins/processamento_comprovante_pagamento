# PROCESSAMENTO COMPROVANTES PAGAMENTO

Geração de comprovantes bancarios de funcionarios listados no liquido folha de cada mês por meio dos retornos bancarios 
de pagamento.

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
* recursos
  * liquido_folha
  * retorno_bancario
* venv - interpretador python
* .gitignore
* README.md
* requirements.txt
* start_processamento.bat 

## Dependências
A aplicação foi desenvolvida utilizando da tecnologia Python 3.9, para o correto funcionamento, é necessario que na 
máquina esteja instalado a versão citado do Python, acesso de leitura e escrita de arquivos nas pastas do projeto, 
usuario com acesso para executar comandos no prompt de comando e acesso à internet para baixar as dependências.

## Executando Projeto

### Recursos
Antes de executar a plicação é preciso preparar os recursos.

#### Liquido Folha
O primeiro é o liquido folha, um arquivo do tipo csv 
que deve ter as seguintes colunas: 

```csv
DESC FILIAL,NOMECOMPLETO,IDFUNCIONARIO,CPF,AGENCIASALARIO,CONTASALARIO,BANCOS,SRC-TOTAL VERBA L01
```
Os dados devem ser separdos por **;** (ponto e virgula), o arquivo deve ser salvo na pasta **recursos/liquido_folha** e 
**na pastas, conter um unico arquivo**, sempre remova o anterior antes de adicionar o novo.

#### Arquivo de Retorno do Banco
Os arquivos de retorno do banco devem ser salvos na pasta **recurso/retorno_bancario** com a extensão **.ret**. Podem ser adicionados 
quantos arquivos forem necessarios para gerar os comprovantes do mês atual.
Antes de salvar os retornos do mês corrente, recomendamos a remoção de todos os arquivos de outros meses, evitando a 
inconsistencia dos dados nos comprovantes gerados. 

### Como executar a aplicação
Na pasta do projeto tem o arquivo **start_processamento.bat** onde deve ser aberto com duplo click do mouse. Esse 
arquivo irá abrir o prompt de comando e então o processamento dos comprovantes iniciará. As etapas serão exibidas na 
tela em forma de logs, é importante acompanhar as mensagens exibidas para saber em que etapa do processamento a 
aplicação está.
Em caso de erro no processamento, solicitamos que tire uma fotografia (print) da tela de execução para melhor 
análise do problema.

### Resultado processamento
Ao término do processamento, os comprovantes estarão salvos na pasta **output/comprovantes** separados por filial.
É gerado tambem o relatorio de **Resultado do Processamento**, localizado na pasta 
**output/relatorio_processamento** onde é informado a quantidade de comprovantes gerados e os funcionarios que nao 
tiveram o comprovante gerado, com base na lista de funcionarios no líquido folha.
