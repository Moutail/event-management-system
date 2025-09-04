#!/usr/bin/env python
"""
Script pour démarrer Celery Worker et Beat
"""
import subprocess
import sys
import os
import time

def check_celery_config():
    """Vérifier la configuration Celery (SQLite)"""
    try:
        # Vérifier que les modules Celery sont disponibles
        import celery
        import django_celery_beat
        print("✅ Configuration Celery (SQLite) prête")
        return True
    except Exception as e:
        print(f"❌ Erreur configuration Celery: {e}")
        return False

def start_celery_worker():
    """Démarrer Celery Worker"""
    print("🚀 Démarrage du Celery Worker...")
    try:
        # Changer vers le répertoire backend
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Démarrer le worker
        process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'event_management', 'worker',
            '--loglevel=info',
            '--concurrency=2'
        ])
        
        print(f"✅ Celery Worker démarré (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Erreur démarrage Celery Worker: {e}")
        return None

def start_celery_beat():
    """Démarrer Celery Beat (planificateur)"""
    print("🚀 Démarrage du Celery Beat...")
    try:
        # Changer vers le répertoire backend
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Démarrer le beat
        process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'event_management', 'beat',
            '--loglevel=info',
            '--schedule=celerybeat-schedule'
        ])
        
        print(f"✅ Celery Beat démarré (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Erreur démarrage Celery Beat: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Configuration Celery pour l'envoi automatique des rappels")
    print("=" * 60)
    
    # Vérifier la configuration Celery
    if not check_celery_config():
        sys.exit(1)
    
    # Démarrer Celery Worker
    worker_process = start_celery_worker()
    if not worker_process:
        sys.exit(1)
    
    # Démarrer Celery Beat
    beat_process = start_celery_beat()
    if not beat_process:
        worker_process.terminate()
        sys.exit(1)
    
    print("\n✅ Celery configuré avec succès!")
    print("📋 Services démarrés:")
    print(f"   - Celery Worker (PID: {worker_process.pid})")
    print(f"   - Celery Beat (PID: {beat_process.pid})")
    print("\n🎯 Les rappels programmés seront maintenant envoyés automatiquement!")
    print("\n💡 Pour arrêter: Ctrl+C")
    
    try:
        # Attendre que les processus se terminent
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt des services...")
        worker_process.terminate()
        beat_process.terminate()
        print("✅ Services arrêtés")

