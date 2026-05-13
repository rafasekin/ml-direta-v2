@echo off
chcp 65001 >nul
title ML Direta - Cloudflare Tunnel

echo.
echo ========================================
echo    🌐 CLOUDFLARE TUNNEL - ML DIRETA
echo ========================================
echo.

echo 📋 Verificando se o Python está instalado...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale o Python primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

echo 🚀 Iniciando script do Cloudflare Tunnel...
echo.

python cloudflared_tunnel.py

echo.
echo ========================================
echo    FIM DO PROGRAMA
echo ========================================
pause
