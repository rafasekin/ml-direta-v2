# Script PowerShell para manter processos persistentes
# ML Direta - Sistema de Gestao Persistente

Write-Host "ML Direta - Sistema de Gestao Persistente" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Criar diretorio de logs se nao existir
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Funcao para iniciar processo com log
function Start-ProcessWithLog {
    param(
        [string]$Name,
        [string]$Executable,
        [string]$Arguments,
        [string]$LogFile
    )
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logPath = "logs\${LogFile}_${timestamp}.log"
    
    Write-Host "[INFO] Iniciando $Name..." -ForegroundColor Yellow
    
    try {
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WindowStyle Hidden -RedirectStandardOutput $logPath -RedirectStandardError $logPath -PassThru
        Write-Host "[OK] $Name iniciado (PID: $($process.Id))" -ForegroundColor Green
        return $process
    }
    catch {
        Write-Host "[ERRO] Falha ao iniciar $Name`: $_" -ForegroundColor Red
        return $null
    }
}

# Iniciar servidor Flask
$flaskProcess = Start-ProcessWithLog -Name "Servidor Flask" -Executable "venv\Scripts\python.exe" -Arguments "app.py" -LogFile "flask"

# Aguardar servidor iniciar
Write-Host "[INFO] Aguardando servidor iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Iniciar Cloudflare Tunnel
$cloudflaredProcess = Start-ProcessWithLog -Name "Cloudflare Tunnel" -Executable ".\cloudflared.exe" -Arguments "tunnel --url http://localhost:3000" -LogFile "cloudflared"

# Aguardar tunnel iniciar
Write-Host "[INFO] Aguardando tunnel iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "[OK] Sistema iniciado com persistencia!" -ForegroundColor Green
Write-Host "[INFO] Logs salvos em: logs\" -ForegroundColor Cyan
Write-Host "[INFO] Acesse: http://localhost:3000" -ForegroundColor Cyan
Write-Host "[INFO] Mantenha esta janela aberta para persistencia" -ForegroundColor Yellow
Write-Host ""

# Loop de monitoramento
while ($true) {
    Start-Sleep -Seconds 300  # 5 minutos
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Verificando processos..." -ForegroundColor Cyan
    
    # Verificar Flask
    if (-not (Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*app.py*"})) {
        Write-Host "[ALERTA] Servidor Flask parado, reiniciando..." -ForegroundColor Red
        $flaskProcess = Start-ProcessWithLog -Name "Servidor Flask" -Executable "venv\Scripts\python.exe" -Arguments "app.py" -LogFile "flask_restart"
    }
    
    # Verificar Cloudflared
    if (-not (Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue)) {
        Write-Host "[ALERTA] Cloudflare Tunnel parado, reiniciando..." -ForegroundColor Red
        $cloudflaredProcess = Start-ProcessWithLog -Name "Cloudflare Tunnel" -Executable ".\cloudflared.exe" -Arguments "tunnel --url http://localhost:3000" -LogFile "cloudflared_restart"
    }
}
