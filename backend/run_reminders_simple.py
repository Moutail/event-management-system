#!/usr/bin/env python
"""
🚀 SCRIPT SIMPLE POUR LES RAPPELS AUTOMATIQUES
Vérifie et envoie les rappels programmés toutes les minutes
"""

import os
import sys
import django
import time
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.tasks import check_scheduled_reminders

def run_reminders_loop():
    """Boucle principale pour vérifier les rappels"""
    print("🚀 DÉMARRAGE DU SYSTÈME DE RAPPELS AUTOMATIQUES")
    print("=" * 60)
    print("✅ Système démarré - Vérification toutes les minutes")
    print("💡 Pour arrêter: Ctrl+C")
    print("=" * 60)
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"⏰ {current_time} - Vérification des rappels...")
            
            try:
                result = check_scheduled_reminders()
                print(f"✅ {current_time} - {result}")
            except Exception as e:
                print(f"❌ {current_time} - Erreur: {e}")
            
            # Attendre 60 secondes
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système de rappels automatiques")
        print("✅ Système arrêté proprement")

if __name__ == "__main__":
    run_reminders_loop()
