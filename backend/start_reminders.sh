#!/bin/bash
echo "🚀 DÉMARRAGE DU SYSTÈME DE RAPPELS AUTOMATIQUES"
echo "================================================"
echo ""
echo "💡 Ce script lance le monitoring des rappels programmés"
echo "💡 Pour arrêter: Ctrl+C"
echo ""

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source .venv/bin/activate

echo ""
echo "🚀 Lancement du monitoring des rappels..."
python run_reminders_manual.py
