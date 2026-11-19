@echo off
title Asistente de Eventos RAA - Servidor local
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
)

echo Iniciando el Asistente de Eventos RAA...
echo La pagina se abrira automaticamente cuando el servidor este listo.
echo.

"%PY%" iniciar_app.py

echo.
echo El servidor se detuvo. Revise los mensajes de arriba.
pause
