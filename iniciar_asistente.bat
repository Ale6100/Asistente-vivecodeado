@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title Antigravity Voice Assistant (agy)
color 0B

echo ========================================================
echo   Iniciando Asistente de Voz para Antigravity CLI (agy)
echo ========================================================
cd /d "%~dp0"

if "%1"=="--clean" goto :clean_env
if "%1"=="--reinstall" goto :clean_env
goto :check_env

:clean_env
echo [*] Eliminando entorno virtual existente para reinstalacion limpia...
if exist "venv" rmdir /s /q "venv"
echo [*] Entorno previo eliminado.

:check_env
if exist "venv\Scripts\python.exe" if exist "venv\.installed" goto :run_assistant

if exist "venv\Scripts\python.exe" (
    echo [*] Se detecto un entorno previo incompleto o una instalacion interrumpida.
    echo [*] Reanudando la instalacion y verificacion de dependencias...
    goto :install_deps
)

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

:install_deps
echo.
echo ========================================================
echo   Instalando dependencias desde requirements.txt
echo   Descarga estimada: ~400 MB en librerias base.
echo   Puede tardar varios minutos segun tu conexion.
echo   Por favor no cierres la ventana ni hagas clic dentro.
echo ========================================================
echo.

venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un fallo al instalar las dependencias.
    echo Verifica tu conexion a internet o si el antivirus bloqueo la descarga.
    echo Si el problema persiste, puedes borrar la carpeta "venv" y reintentar.
    echo.
    pause
    exit /b 1
)

echo OK > "venv\.installed"
echo.
echo [OK] Todas las dependencias se instalaron y verificaron correctamente.
echo.

:run_assistant

venv\Scripts\python.exe main.py
if %errorlevel% neq 0 (
    echo.
    echo [!] El asistente finalizo con codigo %errorlevel%.
)
pause
