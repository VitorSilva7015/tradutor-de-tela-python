@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Iniciando o Tradutor...
python tradutor.py
pause