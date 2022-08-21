@echo off 
echo.
echo ----------------------------------------------------------------------
echo     Instalando dependencias
echo ---------------------------------------------------------------------- 
echo.

pip install -r requirements.txt

echo.
echo ---------------------------------------------------------------------- 
echo     Iniciando execucao do  processamento comprovantes
echo ---------------------------------------------------------------------- 
echo.

cd app
python iniciar_processamento.py

cmd /k