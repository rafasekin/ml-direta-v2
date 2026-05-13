@echo off
chcp 65001 >nul
title ML Direta - Sistema Persistente

echo.
echo ML Direta - Sistema de Gestao Persistente
echo ==========================================
echo.
echo [INFO] Iniciando sistema com persistencia...
echo [AVISO] NAO feche esta janela - processo persistente
echo.

REM Criar diretorio de logs se nao existir
if not exist "logs" mkdir logs

REM Iniciar servidor Flask em background com log
echo [INFO] Iniciando servidor Flask...
start "ML Direta Server" /MIN cmd /c "venv\Scripts\python.exe app.py > logs\flask_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1"

REM Aguardar servidor iniciar
timeout /t 10 /nobreak >nul

REM Iniciar Cloudflare Tunnel em background com log
echo [INFO] Iniciando Cloudflare Tunnel...
start "Cloudflare Tunnel" /MIN cmd /c ".\cloudflared.exe tunnel --url http://localhost:3000 --logfile logs\cloudflared_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log"

REM Aguardar tunnel iniciar
timeout /t 15 /nobreak >nul

echo.
echo [OK] Sistema iniciado com persistencia!
echo [INFO] Verificando status dos processos...

REM Verificar se os processos estao rodando
tasklist | findstr "python.exe" >nul
if %errorlevel% equ 0 (
    echo [OK] Servidor Flask rodando
) else (
    echo [ERRO] Servidor Flask nao encontrado
)

tasklist | findstr "cloudflared.exe" >nul
if %errorlevel% equ 0 (
    echo [OK] Cloudflare Tunnel rodando
) else (
    echo [ERRO] Cloudflare Tunnel nao encontrado
)

echo.
echo [INFO] Logs salvos em: logs\
echo [INFO] Acesse: http://localhost:3000
echo [INFO] Mantenha esta janela aberta para persistencia
echo.

REM Loop infinito para manter o script ativo
:loop
timeout /t 300 /nobreak >nul
echo [%time%] Verificando processos...
tasklist | findstr "python.exe" >nul
if %errorlevel% neq 0 (
    echo [ALERTA] Servidor Flask parado, reiniciando...
    start "ML Direta Server" /MIN cmd /c "venv\Scripts\python.exe app.py >> logs\flask_restart.log 2>&1"
)
tasklist | findstr "cloudflared.exe" >nul
if %errorlevel% neq 0 (
    echo [ALERTA] Cloudflare Tunnel parado, reiniciando...
    start "Cloudflare Tunnel" /MIN cmd /c ".\cloudflared.exe tunnel --url http://localhost:3000 --logfile logs\cloudflared_restart.log"
)
goto loop
