@echo off
chcp 65001 >nul
title ML Direta - Sistema de Gestao Local

echo.
echo ML Direta - Sistema de Gestao Local
echo ==================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale o Python 3.7 ou superior
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo [MENU] Escolha uma opcao:
echo.
echo 1. Iniciar apenas o sistema ML Direta (localhost)
echo 2. Iniciar sistema + Cloudflare Tunnel (acesso externo)
echo 3. Apenas Cloudflare Tunnel (sistema ja rodando)
echo 4. Sair
echo.

set /p opcao="Digite sua opcao [1-4]: "

if "%opcao%"=="1" goto iniciar_sistema
if "%opcao%"=="2" goto iniciar_com_tunnel
if "%opcao%"=="3" goto apenas_tunnel
if "%opcao%"=="4" goto sair

echo [ERRO] Opcao invalida!
pause
goto inicio

:iniciar_sistema
echo.
echo [INFO] Iniciando sistema ML Direta...
echo [INFO] Acesse: http://localhost:3000
echo.
call venv\Scripts\activate.bat && venv\Scripts\python.exe start.py
goto fim

:iniciar_com_tunnel
echo.
echo [INFO] Iniciando sistema ML Direta + Cloudflare Tunnel...
echo [INFO] Aguarde, sera gerada URL publica para acesso externo!
echo.

REM Inicia o sistema em background
start "ML Direta Sistema" cmd /c "call venv\Scripts\activate.bat && venv\Scripts\python.exe start.py"

REM Aguarda um pouco para o sistema iniciar
timeout /t 5 /nobreak >nul

echo [INFO] Sistema iniciado, iniciando Cloudflare Tunnel...
echo.

REM Inicia o tunnel
call venv\Scripts\activate.bat && venv\Scripts\python.exe cloudflared_tunnel.py
goto fim

:apenas_tunnel
echo.
echo [INFO] Iniciando apenas Cloudflare Tunnel...
echo [AVISO] Certifique-se que o sistema ja esta rodando em localhost:3000
echo.
call venv\Scripts\activate.bat && venv\Scripts\python.exe cloudflared_tunnel.py
goto fim

:sair
echo [INFO] Saindo...
exit /b 0

:fim
echo.
echo [INFO] Operacao finalizada.
pause
