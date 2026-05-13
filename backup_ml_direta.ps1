# Sistema de Backup Automático - ML Direta
# Cria backup completo diário e envia para Google Drive

# Configurações
$SourcePath = "C:\Users\ICOMON\Documents\Ml direta"
$DestinationPath = "G:\Meu Drive\SISTEMAS\MALA DIRETA"
$LogPath = "C:\Users\ICOMON\Documents\Ml direta\logs"
$BackupRetentionDays = 30  # Manter backups por 30 dias

# Criar diretório de logs se não existir
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

# Função de log
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logFile = "$LogPath\backup_$(Get-Date -Format 'yyyy-MM').log"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry -ForegroundColor $(switch($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    })
    
    Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
}

# Função principal de backup
function Start-MLDiretaBackup {
    try {
        Write-Log "Iniciando backup do ML Direta" "INFO"
        
        # Verificar se o diretório de origem existe
        if (-not (Test-Path $SourcePath)) {
            Write-Log "Diretório de origem não encontrado: $SourcePath" "ERROR"
            return $false
        }
        
        # Verificar se o diretório de destino existe
        if (-not (Test-Path $DestinationPath)) {
            Write-Log "Criando diretório de destino: $DestinationPath" "WARNING"
            New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
        }
        
        # Gerar nome do arquivo de backup
        $dateStamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
        $backupFileName = "ML_Direta_Backup_$dateStamp.zip"
        $backupFilePath = "$DestinationPath\$backupFileName"
        
        Write-Log "Criando backup: $backupFileName" "INFO"
        
        # Comprimir a pasta completa (excluindo arquivos em uso)
        try {
            Write-Log "Verificando arquivos em uso..." "INFO"
            
            # Criar diretório temporário para backup
            $tempDir = "$env:TEMP\ML_Direta_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            
            # Copiar arquivos excluindo os bloqueados
            Write-Log "Copiando arquivos para diretório temporário..." "INFO"
            $copiedFiles = 0
            $skippedFiles = 0
            
            Get-ChildItem -Path $SourcePath -Recurse | ForEach-Object {
                try {
                    $relativePath = $_.FullName.Replace($SourcePath, "").TrimStart('\')
                    $destinationPath = Join-Path $tempDir $relativePath
                    
                    if ($_.PSIsContainer) {
                        # Criar diretório
                        if (-not (Test-Path $destinationPath)) {
                            New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
                        }
                    } else {
                        # Tentar copiar arquivo
                        try {
                            # Verificar se arquivo está bloqueado
                            $fileStream = $_.Open([System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
                            $fileStream.Close()
                            
                            # Se não estiver bloqueado, copiar
                            $destDir = Split-Path $destinationPath -Parent
                            if (-not (Test-Path $destDir)) {
                                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                            }
                            Copy-Item -Path $_.FullName -Destination $destinationPath -Force
                            $copiedFiles++
                        }
                        catch {
                            # Arquivo está bloqueado, pular
                            Write-Log "Arquivo bloqueado, pulando: $($_.Name)" "WARNING"
                            $skippedFiles++
                        }
                    }
                }
                catch {
                    Write-Log "Erro ao processar $($_.FullName): $_" "WARNING"
                    $skippedFiles++
                }
            }
            
            Write-Log "Arquivos copiados: $copiedFiles, Pulados: $skippedFiles" "INFO"
            
            # Comprimir o diretório temporário
            Write-Log "Compactando diretório temporário..." "INFO"
            Add-Type -AssemblyName "System.IO.Compression.FileSystem"
            [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $backupFilePath)
            
            # Limpar diretório temporário
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            
            # Verificar se o arquivo foi criado
            if (Test-Path $backupFilePath) {
                $fileSize = [math]::Round((Get-Item $backupFilePath).Length / 1MB, 2)
                Write-Log "Backup criado com sucesso: $backupFileName ($fileSize MB)" "SUCCESS"
            } else {
                Write-Log "Falha ao criar arquivo de backup" "ERROR"
                return $false
            }
        }
        catch {
            Write-Log "Erro durante compressão: $_" "ERROR"
            
            # Tentar método alternativo com exclusão de arquivos específicos
            try {
                Write-Log "Tentando método alternativo de compressão..." "WARNING"
                
                # Criar lista de exclusões
                $excludeFiles = @("*.log", "*.tmp", "cloudflared.exe", "venv\Scripts\python.exe")
                $includeFiles = Get-ChildItem -Path $SourcePath -Recurse -File | Where-Object {
                    $exclude = $false
                    foreach ($pattern in $excludeFiles) {
                        if ($_.Name -like $pattern) {
                            $exclude = $true
                            break
                        }
                    }
                    -not $exclude
                }
                
                if ($includeFiles.Count -gt 0) {
                    Compress-Archive -Path $includeFiles.FullName -DestinationPath $backupFilePath -Force
                    
                    if (Test-Path $backupFilePath) {
                        $fileSize = [math]::Round((Get-Item $backupFilePath).Length / 1MB, 2)
                        Write-Log "Backup criado com método alternativo: $backupFileName ($fileSize MB)" "SUCCESS"
                    } else {
                        Write-Log "Falha em ambos os métodos de compressão" "ERROR"
                        return $false
                    }
                } else {
                    Write-Log "Nenhum arquivo válido para backup" "ERROR"
                    return $false
                }
            }
            catch {
                Write-Log "Falha no método alternativo: $_" "ERROR"
                return $false
            }
        }
        
        # Limpar backups antigos
        Write-Log "Limpando backups antigos (mais de $BackupRetentionDays dias)" "INFO"
        $cutoffDate = (Get-Date).AddDays(-$BackupRetentionDays)
        $oldBackups = Get-ChildItem -Path $DestinationPath -Filter "ML_Direta_Backup_*.zip" | Where-Object { $_.CreationTime -lt $cutoffDate }
        
        if ($oldBackups) {
            foreach ($backup in $oldBackups) {
                try {
                    Remove-Item $backup.FullName -Force
                    Write-Log "Removido backup antigo: $($backup.Name)" "INFO"
                }
                catch {
                    Write-Log "Erro ao remover backup antigo $($backup.Name): $_" "WARNING"
                }
            }
        } else {
            Write-Log "Nenhum backup antigo encontrado para remover" "INFO"
        }
        
        # Verificar integridade do backup
        Write-Log "Verificando integridade do backup" "INFO"
        $backupInfo = Get-Item $backupFilePath
        if ($backupInfo.Length -gt 0) {
            Write-Log "Backup verificado e válido" "SUCCESS"
            Write-Log "Backup concluído com sucesso! Arquivo: $backupFilePath" "SUCCESS"
            return $true
        } else {
            Write-Log "Backup parece estar corrompido (tamanho 0)" "ERROR"
            Remove-Item $backupFilePath -Force -ErrorAction SilentlyContinue
            return $false
        }
    }
    catch {
        Write-Log "Erro geral durante backup: $_" "ERROR"
        return $false
    }
}

# Função para verificar espaço em disco
function Test-DiskSpace {
    $destinationDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "G:" }
    
    if ($destinationDrive) {
        $freeSpaceGB = [math]::Round($destinationDrive.FreeSpace / 1GB, 2)
        Write-Log "Espaço livre no drive G: $freeSpaceGB GB" "INFO"
        
        if ($freeSpaceGB -lt 1) {
            Write-Log "ATENÇÃO: Espaço em disco baixo ($freeSpaceGB GB)" "WARNING"
        }
        
        return $freeSpaceGB
    } else {
        Write-Log "Drive G: não encontrado" "ERROR"
        return $null
    }
}

# Execução principal
Write-Log "=== SISTEMA DE BACKUP ML DIRETA ===" "INFO"
Write-Log "Iniciando processo de backup em $(Get-Date)" "INFO"

# Verificar espaço em disco
Test-DiskSpace

# Executar backup
$backupResult = Start-MLDiretaBackup

if ($backupResult) {
    Write-Log "Backup automático concluído com sucesso!" "SUCCESS"
    exit 0
} else {
    Write-Log "Falha no backup automático" "ERROR"
    exit 1
}
