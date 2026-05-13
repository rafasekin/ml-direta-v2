@echo off
chcp 65001 >nul
title ML Direta - Instalar Backup Automático

echo.
echo ML Direta - Instalar Backup Automático
echo =====================================
echo.
echo Este script irá configurar o backup automático diário do sistema.
echo O backup será executado todos os dias às 02:00 da manhã.
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Execute este script como Administrador!
    echo [INFO] Clique direito no arquivo e "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Executando como Administrador
echo.

REM Verificar se o PowerShell script existe
if not exist "backup_ml_direta.ps1" (
    echo [ERRO] Script de backup não encontrado: backup_ml_direta.ps1
    echo [INFO] Verifique se o arquivo está no mesmo diretório
    pause
    exit /b 1
)

REM Verificar se o diretório de destino existe
if not exist "G:\Meu Drive\SISTEMAS\MALA DIRETA" (
    echo [AVISO] Diretório de destino não encontrado
    echo [INFO] Criando diretório: G:\Meu Drive\SISTEMAS\MALA DIRETA
    mkdir "G:\Meu Drive\SISTEMAS\MALA DIRETA" 2>nul
    if errorlevel 1 (
        echo [ERRO] Não foi possível criar o diretório de destino
        echo [INFO] Verifique se o drive G: está disponível
        pause
        exit /b 1
    )
)

echo [INFO] Configurando tarefa agendada...
echo.

REM Executar o script PowerShell
powershell -ExecutionPolicy Bypass -File "agendar_backup.ps1"

echo.
echo [INFO] Processo concluído!
echo.
echo [RESUMO DA CONFIGURAÇÃO:]
echo   - Backup diário às 02:00
echo   - Origem: C:\Users\ICOMON\Documents\Ml direta
echo   - Destino: G:\Meu Drive\SISTEMAS\MALA DIRETA
echo   - Retenção: 30 dias
echo   - Logs: C:\Users\ICOMON\Documents\Ml direta\logs\
echo.
echo [PARA TESTAR MANUALMENTE:]
echo   powershell -ExecutionPolicy Bypass -File "backup_ml_direta.ps1"
echo.
echo [PARA GERENCIAR A TAREFA:]
echo   Abrir "Agendador de Tarefas" do Windows
echo   Procurar por "ML Direta Backup Diario"
echo.

pause
