#!/usr/bin/env python
"""
🚀 DÉMARRAGE DU SYSTÈME DE RAPPELS AUTOMATIQUES
Script simple pour démarrer Celery Worker et Beat
"""

import os
import sys
import subprocess
import time

def start_reminders_system():
    """Démarrer le système de rappels automatiques"""
    print("🎯 DÉMARRAGE DU SYSTÈME DE RAPPELS AUTOMATIQUES")
    print("=" * 60)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('manage.py'):
        print("❌ Erreur: manage.py non trouvé. Assurez-vous d'être dans le dossier backend.")
        return False
    
    print("✅ Répertoire backend détecté")
    
    # Démarrer Celery Worker
    print("\n🚀 Démarrage du Celery Worker...")
    try:
        worker_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'event_management', 'worker',
            '--loglevel=info',
            '--concurrency=1'
        ])
        print(f"✅ Celery Worker démarré (PID: {worker_process.pid})")
    except Exception as e:
        print(f"❌ Erreur démarrage Worker: {e}")
        return False
    
    # Attendre un peu
    time.sleep(2)
    
    # Démarrer Celery Beat
    print("\n🚀 Démarrage du Celery Beat...")
    try:
        beat_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'event_management', 'beat',
            '--loglevel=info',
            '--schedule=celerybeat-schedule'
        ])
        print(f"✅ Celery Beat démarré (PID: {beat_process.pid})")
    except Exception as e:
        print(f"❌ Erreur démarrage Beat: {e}")
        worker_process.terminate()
        return False
    
    print("\n" + "=" * 60)
    print("🎉 SYSTÈME DE RAPPELS AUTOMATIQUES DÉMARRÉ!")
    print("=" * 60)
    print("📋 Services actifs:")
    print(f"   - Celery Worker (PID: {worker_process.pid})")
    print(f"   - Celery Beat (PID: {beat_process.pid})")
    print("\n🎯 Fonctionnalités:")
    print("   ✅ Rappels programmés automatiques")
    print("   ✅ Vérification toutes les minutes")
    print("   ✅ Envoi par email et SMS")
    print("   ✅ Gestion des erreurs")
    print("\n💡 Pour arrêter: Ctrl+C")
    print("=" * 60)
    
    try:
        # Attendre que les processus se terminent
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt des services...")
        worker_process.terminate()
        beat_process.terminate()
        print("✅ Services arrêtés")
        return True

if __name__ == "__main__":
    try:
        start_reminders_system()
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        sys.exit(1)
