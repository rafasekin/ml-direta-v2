@echo off
chcp 65001 >nul
title ML Direta - Instalar Servico Windows

echo.
echo ML Direta - Instalar Servico Windows Persistente
echo ================================================
echo.

REM Verificar se esta executando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Execute este script como Administrador!
    echo [INFO] Clique direito no arquivo e "Executar como administrador"
    pause
    exit /b 1
)

REM Baixar NSSM (Non-Sucking Service Manager)
echo [INFO] Baixando NSSM...
powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"

REM Extrair NSSM
echo [INFO] Extraindo NSSM...
powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.' -Force"

REM Copiar NSSM para diretorio do sistema
echo [INFO] Instalando NSSM...
copy "nssm-2.24\win64\nssm.exe" "C:\Windows\System32\" >nul

REM Criar servico para o Flask
echo [INFO] Criando servico ML Direta Flask...
nssm install "ML Direta Flask" "%cd%\venv\Scripts\python.exe"
nssm set "ML Direta Flask" Arguments "%cd%\app.py"
nssm set "ML Direta Flask" DisplayName "ML Direta - Servidor Flask"
nssm set "ML Direta Flask" Description "Sistema de Gestao ML Direta - Servidor Flask"
nssm set "ML Direta Flask" Start SERVICE_AUTO_START
nssm set "ML Direta Flask" AppDirectory "%cd%"
nssm set "ML Direta Flask" AppStdout "%cd%\logs\flask_service.log"
nssm set "ML Direta Flask" AppStderr "%cd%\logs\flask_service.log"

REM Criar servico para o Cloudflare Tunnel
echo [INFO] Criando servico ML Direta Tunnel...
nssm install "ML Direta Tunnel" "%cd%\cloudflared.exe"
nssm set "ML Direta Tunnel" Arguments "tunnel --url http://localhost:3000"
nssm set "ML Direta Tunnel" DisplayName "ML Direta - Cloudflare Tunnel"
nssm set "ML Direta Tunnel" Description "Sistema de Gestao ML Direta - Cloudflare Tunnel"
nssm set "ML Direta Tunnel" Start SERVICE_AUTO_START
nssm set "ML Direta Tunnel" AppDirectory "%cd%"
nssm set "ML Direta Tunnel" AppStdout "%cd%\logs\cloudflared_service.log"
nssm set "ML Direta Tunnel" AppStderr "%cd%\logs\cloudflared_service.log"

REM Criar diretorio de logs
if not exist "logs" mkdir logs

REM Iniciar os servicos
echo [INFO] Iniciando servicos...
net start "ML Direta Flask"
net start "ML Direta Tunnel"

REM Limpar arquivos temporarios
echo [INFO] Limpando arquivos temporarios...
rmdir /s /q "nssm-2.24" >nul 2>&1
del "nssm.zip" >nul 2>&1

echo.
echo [OK] Servicos instalados e iniciados com sucesso!
echo [INFO] Os servicos iniciaram automaticamente com o Windows
echo [INFO] Para gerenciar os servicos: services.msc
echo [INFO] Logs em: logs\
echo.
echo [COMANDOS UTEIS:]
echo   net stop "ML Direta Flask"     - Para servidor Flask
echo   net start "ML Direta Flask"    - Iniciar servidor Flask
echo   net stop "ML Direta Tunnel"    - Para tunnel
echo   net start "ML Direta Tunnel"   - Iniciar tunnel
echo   nssm remove "ML Direta Flask"  - Remover servico Flask
echo   nssm remove "ML Direta Tunnel" - Remover servico tunnel
echo.

pause
