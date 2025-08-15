#!/bin/bash
# Script Bash pour exécuter automatiquement les notifications d'événements
# Exécute la commande send_event_notifications toutes les 15 minutes

INTERVAL_MINUTES=${1:-15}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/notifications.log"

echo "🚀 Démarrage du service de notifications automatiques..."
echo "📍 Répertoire: $SCRIPT_DIR"
echo "📝 Log: $LOG_FILE"
echo "⏰ Intervalle: $INTERVAL_MINUTES minutes"
echo "🛑 Arrêt: Ctrl+C"
echo ""

# Fonction pour exécuter la commande Django
run_notification_command() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Activer l'environnement virtuel
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    # Exécuter la commande et capturer la sortie
    if output=$(python manage.py send_event_notifications 2>&1); then
        # Succès
        log_entry="[$timestamp] SUCCESS: $output"
        echo -e "\033[32m$log_entry\033[0m"
        echo "$log_entry" >> "$LOG_FILE"
    else
        # Erreur
        log_entry="[$timestamp] ERROR: $output"
        echo -e "\033[31m$log_entry\033[0m"
        echo "$log_entry" >> "$LOG_FILE"
    fi
}

# Gérer l'arrêt propre avec Ctrl+C
trap 'echo -e "\n🛑 Service arrêté par l'\''utilisateur."; exit 0' INT

# Boucle principale
while true; do
    run_notification_command
    
    # Calculer et afficher l'heure de la prochaine exécution
    next_run=$(date -d "+${INTERVAL_MINUTES} minutes" '+%H:%M:%S' 2>/dev/null || date -v +${INTERVAL_MINUTES}M '+%H:%M:%S')
    echo -e "\033[36m⏳ Prochaine exécution: $next_run\033[0m"
    
    # Attendre l'intervalle spécifié
    sleep $((INTERVAL_MINUTES * 60))
done



