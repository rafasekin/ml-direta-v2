# Script para agendar backup automático do ML Direta
# Configura tarefa no Task Scheduler para execução diária

# Configurações
$ScriptPath = "C:\Users\ICOMON\Documents\Ml direta\backup_ml_direta.ps1"
$TaskName = "ML Direta Backup Diario"
$Description = "Backup automático diário do sistema ML Direta para Google Drive"
$RunTime = "02:00"  # 2:00 da manhã
$DaysOfWeek = @("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# Verificar se está executando como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Função para criar a tarefa agendada
function New-BackupScheduledTask {
    try {
        Write-Host "Criando tarefa agendada: $TaskName" -ForegroundColor Green
        
        # Verificar se a tarefa já existe
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        
        if ($existingTask) {
            Write-Host "Tarefa '$TaskName' já existe. Removendo para recriar..." -ForegroundColor Yellow
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        
        # Criar o objeto de ação
        $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`""
        
        # Criar o objeto de gatilho (diário às 2:00)
        $trigger = New-ScheduledTaskTrigger -Daily -At $RunTime
        
        # Criar o objeto de configuração
        $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Hours 2)
        
        # Configurar o usuário para executar a tarefa
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
        
        # Registrar a tarefa
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $Description -Force
        
        Write-Host "Tarefa agendada criada com sucesso!" -ForegroundColor Green
        Write-Host "Detalhes da tarefa:" -ForegroundColor Cyan
        Write-Host "  Nome: $TaskName" -ForegroundColor White
        Write-Host "  Horário: $RunTime (diário)" -ForegroundColor White
        Write-Host "  Script: $ScriptPath" -ForegroundColor White
        Write-Host "  Usuário: SYSTEM" -ForegroundColor White
        
        return $true
    }
    catch {
        Write-Host "Erro ao criar tarefa agendada: $_" -ForegroundColor Red
        return $false
    }
}

# Função para verificar a tarefa criada
function Get-BackupTaskStatus {
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        
        if ($task) {
            Write-Host "`nStatus da tarefa agendada:" -ForegroundColor Cyan
            Write-Host "  Nome: $($task.TaskName)" -ForegroundColor White
            Write-Host "  Estado: $($task.State)" -ForegroundColor White
            Write-Host "  Descrição: $($task.Description)" -ForegroundColor White
            
            if ($task.Triggers) {
                Write-Host "  Gatilhos:" -ForegroundColor White
                foreach ($trigger in $task.Triggers) {
                    Write-Host "    - $($trigger.Frequency) às $($trigger.StartBoundary)" -ForegroundColor Gray
                }
            }
            
            if ($task.Actions) {
                Write-Host "  Ação:" -ForegroundColor White
                foreach ($action in $task.Actions) {
                    Write-Host "    - $($action.Execute) $($action.Arguments)" -ForegroundColor Gray
                }
            }
            
            return $true
        } else {
            Write-Host "Tarefa não encontrada" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Erro ao verificar tarefa: $_" -ForegroundColor Red
        return $false
    }
}

# Função para remover a tarefa
function Remove-BackupScheduledTask {
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        
        if ($task) {
            Write-Host "Removendo tarefa agendada: $TaskName" -ForegroundColor Yellow
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Host "Tarefa removida com sucesso!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Tarefa não encontrada para remover" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Erro ao remover tarefa: $_" -ForegroundColor Red
        return $false
    }
}

# Menu principal
function Show-Menu {
    Write-Host "`n=== AGENDAMENTO DE BACKUP ML DIRETA ===" -ForegroundColor Cyan
    Write-Host "1. Criar tarefa agendada (recomendado)" -ForegroundColor White
    Write-Host "2. Verificar status da tarefa" -ForegroundColor White
    Write-Host "3. Remover tarefa agendada" -ForegroundColor White
    Write-Host "4. Sair" -ForegroundColor White
    Write-Host "======================================" -ForegroundColor Cyan
}

# Execução principal
Clear-Host
Write-Host "SISTEMA DE AGENDAMENTO DE BACKUP - ML DIRETA" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Verificar privilégios de administrador
if (-not (Test-Administrator)) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com o botão direito no script e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Verificar se o script de backup existe
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERRO: Script de backup não encontrado em: $ScriptPath" -ForegroundColor Red
    Write-Host "Verifique se o arquivo backup_ml_direta.ps1 existe no diretório correto." -ForegroundColor Yellow
    exit 1
}

Write-Host "Privilégios de administrador confirmados!" -ForegroundColor Green
Write-Host "Script de backup encontrado em: $ScriptPath" -ForegroundColor Green

do {
    Show-Menu
    $choice = Read-Host "`nDigite sua opção (1-4)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nCriando tarefa agendada..." -ForegroundColor Yellow
            if (New-BackupScheduledTask) {
                Get-BackupTaskStatus
            }
        }
        "2" {
            Write-Host "`nVerificando status da tarefa..." -ForegroundColor Yellow
            Get-BackupTaskStatus
        }
        "3" {
            Write-Host "`nRemovendo tarefa agendada..." -ForegroundColor Yellow
            Remove-BackupScheduledTask
        }
        "4" {
            Write-Host "`nSaindo..." -ForegroundColor Cyan
            break
        }
        default {
            Write-Host "`nOpção inválida! Tente novamente." -ForegroundColor Red
        }
    }
    
    if ($choice -ne "4") {
        Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Cyan
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} while ($choice -ne "4")

Write-Host "`nOperação concluída!" -ForegroundColor Green
