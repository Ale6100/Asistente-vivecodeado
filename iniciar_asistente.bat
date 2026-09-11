@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title Antigravity Voice Assistant (agy)
color 0B

echo ========================================================
echo   Iniciando Asistente de Voz para Antigravity CLI (agy)
echo ========================================================
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" goto :run_assistant

echo [*] Configurando el entorno virtual por primera vez...

py -3 -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "SYSTEM_PYTHON=py -3"
    goto :create_venv
)

python -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "SYSTEM_PYTHON=python"
    goto :create_venv
)

echo.
echo [ERROR] No se encontro una instalacion funcional de Python en el sistema.
echo Por favor instala Python 3.10 o superior desde: https://www.python.org/downloads/
echo IMPORTANTE: Durante la instalacion, marca la casilla "Add python.exe to PATH".
echo.
pause
exit /b 1

:create_venv
echo [!] Creando entorno virtual local (venv)...
%SYSTEM_PYTHON% -m venv venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No se pudo crear el entorno virtual venv.
    pause
    exit /b 1
)

echo [*] Instalando dependencias del proyecto desde requirements.txt...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] Ocurrio un inconveniente al instalar algunas dependencias.
)

:run_assistant
venv\Scripts\python.exe main.py
if %errorlevel% neq 0 (
    echo.
    echo [!] El asistente finalizo con codigo %errorlevel%.
)
pause
