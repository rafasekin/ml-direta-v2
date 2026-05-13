# Script de Diagnostico - ML Direta
# Identifica por que os processos estao fechando

Write-Host "DIAGNOSTICO - ML Direta" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar configuracoes de energia
Write-Host "1. CONFIGURACOES DE ENERGIA:" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow

$powerSettings = powercfg /query
$sleepSettings = $powerSettings | Select-String "Suspender depois de"
$hibernateSettings = $powerSettings | Select-String "Hibernar"

Write-Host "Configuracoes de suspensao:" -ForegroundColor Gray
$sleepSettings | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host "Configuracoes de hibernacao:" -ForegroundColor Gray
$hibernateSettings | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# 2. Verificar eventos do sistema
Write-Host ""
Write-Host "2. EVENTOS RECENTES DO SISTEMA:" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

try {
    $events = Get-WinEvent -LogName System -MaxEvents 10 | Where-Object { $_.TimeCreated -gt (Get-Date).AddHours(-2) }
    if ($events) {
        $events | ForEach-Object {
            Write-Host "  [$($_.TimeCreated)] $($_.Id) - $($_.LevelDisplayName): $($_.Message)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Nenhum evento recente encontrado" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Erro ao ler eventos: $_" -ForegroundColor Red
}

# 3. Verificar processos ativos
Write-Host ""
Write-Host "3. PROCESSOS ATIVOS:" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Yellow

$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
$cloudflaredProcesses = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue

Write-Host "Processos Python:" -ForegroundColor Gray
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id), CPU: $($_.CPU), Memoria: $([math]::Round($_.WorkingSet/1MB, 2))MB" -ForegroundColor Gray
    }
} else {
    Write-Host "  Nenhum processo Python encontrado" -ForegroundColor Red
}

Write-Host "Processos Cloudflared:" -ForegroundColor Gray
if ($cloudflaredProcesses) {
    $cloudflaredProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id), CPU: $($_.CPU), Memoria: $([math]::Round($_.WorkingSet/1MB, 2))MB" -ForegroundColor Gray
    }
} else {
    Write-Host "  Nenhum processo Cloudflared encontrado" -ForegroundColor Red
}

# 4. Verificar portas em uso
Write-Host ""
Write-Host "4. PORTAS EM USO:" -ForegroundColor Yellow
Write-Host "----------------" -ForegroundColor Yellow

try {
    $port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    if ($port3000) {
        Write-Host "Porta 3000 em uso:" -ForegroundColor Green
        $port3000 | ForEach-Object {
            $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
            Write-Host "  PID: $($_.OwningProcess), Processo: $($process.ProcessName), Estado: $($_.State)" -ForegroundColor Gray
        }
    } else {
        Write-Host "Porta 3000 nao esta em uso" -ForegroundColor Red
    }
} catch {
    Write-Host "Erro ao verificar portas: $_" -ForegroundColor Red
}

# 5. Verificar logs de aplicacao
Write-Host ""
Write-Host "5. LOGS DE APLICACAO:" -ForegroundColor Yellow
Write-Host "--------------------" -ForegroundColor Yellow

if (Test-Path "logs") {
    $logFiles = Get-ChildItem "logs" -Filter "*.log" | Sort-Object LastWriteTime -Descending
    if ($logFiles) {
        Write-Host "Arquivos de log encontrados:" -ForegroundColor Gray
        $logFiles | ForEach-Object {
            Write-Host "  $($_.Name) - $($_.LastWriteTime) - $([math]::Round($_.Length/1KB, 2))KB" -ForegroundColor Gray
        }
    } else {
        Write-Host "Nenhum arquivo de log encontrado" -ForegroundColor Gray
    }
} else {
    Write-Host "Diretorio de logs nao existe" -ForegroundColor Gray
}

# 6. Verificar configuracoes de rede
Write-Host ""
Write-Host "6. CONFIGURACOES DE REDE:" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow

try {
    $networkAdapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    Write-Host "Adaptadores de rede ativos:" -ForegroundColor Gray
    $networkAdapters | ForEach-Object {
        Write-Host "  $($_.Name) - $($_.InterfaceDescription)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Erro ao verificar adaptadores de rede: $_" -ForegroundColor Red
}

# 7. Recomendacoes
Write-Host ""
Write-Host "7. RECOMENDACOES:" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Yellow

Write-Host "Solucoes possiveis:" -ForegroundColor Green
Write-Host "1. Execute o script install_service.bat como Administrador" -ForegroundColor White
Write-Host "2. Use start_persistent.ps1 para monitoramento continuo" -ForegroundColor White
Write-Host "3. Verifique se o Windows esta entrando em suspensao" -ForegroundColor White
Write-Host "4. Configure as opcoes de energia para 'Nunca' suspender" -ForegroundColor White
Write-Host "5. Verifique se há atualizacoes automaticas reiniciando o sistema" -ForegroundColor White

Write-Host ""
Write-Host "Diagnostico concluido!" -ForegroundColor Green
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
