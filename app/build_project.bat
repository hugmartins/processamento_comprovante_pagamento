@echo off
echo.
echo ----------------------------------------------------------------------
echo     Iniciando build
echo ----------------------------------------------------------------------
echo.

echo.
echo ----------------------------------------------------------------------
echo     Excluindo versao anterior
echo ----------------------------------------------------------------------
echo.

if exist processamento_comprovante_pagamento_build rmdir /s /q processamento_comprovante_pagamento_build
if exist start_processamento_arq_ban.exe del /s /q start_processamento_arq_ban.exe

del /s /q ..\jasper_report\datasource\*.*

echo.
echo ----------------------------------------------------------------------
echo     Gerando start_processamento_arq_ban.exe
echo ----------------------------------------------------------------------
echo.

pyinstaller --onefile --name start_processamento_arq_ban iniciar_processamento.py

echo.
echo ----------------------------------------------------------------------
echo     Excluindo arquivos desnecessarios
echo ----------------------------------------------------------------------
echo.

rmdir /s /q build
del /s /q start_processamento_arq_ban.spec

move dist\*.*
rmdir /s /q dist

echo.
echo ----------------------------------------------------------------------
echo     Build do projeto
echo ----------------------------------------------------------------------
echo.

mkdir processamento_comprovante_pagamento_build
mkdir processamento_comprovante_pagamento_build\output\comprovantes\
mkdir processamento_comprovante_pagamento_build\output\relatorio_inconsistencias\
mkdir processamento_comprovante_pagamento_build\output\resultado_processamento_comprovantes\

mkdir processamento_comprovante_pagamento_build\recursos\liquido_folha\
mkdir processamento_comprovante_pagamento_build\recursos\previa_pagamento\
mkdir processamento_comprovante_pagamento_build\recursos\retorno_comprovante_folpag\

xcopy  ..\README.md processamento_comprovante_pagamento_build

xcopy /s/e ..\jasper_report processamento_comprovante_pagamento_build\jasper_report\

REM xcopy /s/e ..\recursos processamento_comprovante_pagamento_build\recursos\
REM xcopy /s/e ..\output processamento_comprovante_pagamento_build\output\

xcopy /s/e dto\ processamento_comprovante_pagamento_build\app\dto\
xcopy /s/e service\ processamento_comprovante_pagamento_build\app\service\
xcopy /s/e utils\ processamento_comprovante_pagamento_build\app\utils\

xcopy  __init__.py processamento_comprovante_pagamento_build\app
xcopy  iniciar_processamento.py processamento_comprovante_pagamento_build\app
move  start_processamento_arq_ban.exe processamento_comprovante_pagamento_build\app

cmd /k