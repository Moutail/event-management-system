# Script PowerShell pour exécuter automatiquement les notifications d'événements
# Exécute la commande send_event_notifications toutes les 15 minutes

param(
    [int]$IntervalMinutes = 15
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = $scriptPath
$logFile = Join-Path $projectPath "notifications.log"

Write-Host "🚀 Démarrage du service de notifications automatiques..."
Write-Host "📍 Répertoire: $projectPath"
Write-Host "📝 Log: $logFile"
Write-Host "⏰ Intervalle: $IntervalMinutes minutes"
Write-Host "🛑 Arrêt: Ctrl+C"
Write-Host ""

# Fonction pour exécuter la commande Django
function Invoke-NotificationCommand {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    try {
        # Activer l'environnement virtuel et exécuter la commande
        & ".\.venv\Scripts\Activate.ps1"
        $output = python manage.py send_event_notifications 2>&1
        
        # Log du succès
        $logEntry = "[$timestamp] SUCCESS: $output"
        Write-Host $logEntry -ForegroundColor Green
        Add-Content -Path $logFile -Value $logEntry
        
    } catch {
        # Log de l'erreur
        $logEntry = "[$timestamp] ERROR: $($_.Exception.Message)"
        Write-Host $logEntry -ForegroundColor Red
        Add-Content -Path $logFile -Value $logEntry
    }
}

# Boucle principale
try {
    while ($true) {
        Invoke-NotificationCommand
        
        # Attendre l'intervalle spécifié
        $nextRun = (Get-Date).AddMinutes($IntervalMinutes)
        Write-Host "⏳ Prochaine exécution: $($nextRun.ToString('HH:mm:ss'))" -ForegroundColor Cyan
        Start-Sleep -Seconds ($IntervalMinutes * 60)
    }
} catch {
    Write-Host "🛑 Service arrêté: $($_.Exception.Message)" -ForegroundColor Yellow
} finally {
    Write-Host "👋 Service de notifications terminé." -ForegroundColor Yellow
}



