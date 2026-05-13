@echo off
chcp 65001 >nul
title ML Direta - Iniciar com Acesso Externo

echo.
echo 🌐 ML Direta - Iniciando com Acesso Externo
echo ============================================
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

echo [INFO] Iniciando sistema ML Direta + Cloudflare Tunnel...
echo [INFO] Sistema local: http://localhost:3000
echo [INFO] URL publica: sera gerada em instantes...
echo.
echo 📋 Mantenha esta janela aberta para manter o acesso externo ativo
echo ⏹️  Feche esta janela para desativar o acesso externo
echo.

REM Inicia o sistema em background
start "ML Direta Sistema" cmd /c "python start.py"

REM Aguarda um pouco para o sistema iniciar
timeout /t 5 /nobreak >nul

echo [INFO] Sistema iniciado, iniciando Cloudflare Tunnel...
echo.

REM Inicia o tunnel
python cloudflared_tunnel.py

echo.
echo [INFO] Acesso externo desativado.
pause
