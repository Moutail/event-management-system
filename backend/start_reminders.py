#!/usr/bin/env python
"""
🚀 SCRIPT DE DÉMARRAGE DES RAPPELS AUTOMATIQUES
Démarre Celery Worker et Celery Beat pour les rappels automatiques
"""

import os
import sys
import subprocess
import time

def check_celery_config():
    """Vérifier que Celery est configuré"""
    print("🔍 Vérification de la configuration Celery...")
    try:
        import celery
        import django_celery_beat
        print("✅ Modules Celery installés")
        return True
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
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
            '--concurrency=1'
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

def test_reminder_system():
    """Tester le système de rappels"""
    print("🧪 Test du système de rappels...")
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
        django.setup()
        
        from events.tasks import check_scheduled_reminders
        from events.models import CustomReminder
        
        # Compter les rappels programmés
        scheduled_reminders = CustomReminder.objects.filter(status='scheduled').count()
        print(f"📊 Rappels programmés: {scheduled_reminders}")
        
        # Tester la tâche de vérification
        result = check_scheduled_reminders()
        print(f"✅ Test réussi: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    print("🎯 SYSTÈME DE RAPPELS AUTOMATIQUES")
    print("=" * 50)
    
    # Vérifier la configuration Celery
    if not check_celery_config():
        sys.exit(1)
    
    # Tester le système
    if not test_reminder_system():
        print("⚠️ Problème détecté dans le système de rappels")
    
    # Démarrer Celery Worker
    worker_process = start_celery_worker()
    if not worker_process:
        sys.exit(1)
    
    # Attendre un peu pour que le worker démarre
    time.sleep(2)
    
    # Démarrer Celery Beat
    beat_process = start_celery_beat()
    if not beat_process:
        worker_process.terminate()
        sys.exit(1)
    
    print("\n✅ SYSTÈME DE RAPPELS AUTOMATIQUES DÉMARRÉ!")
    print("📋 Services actifs:")
    print(f"   - Celery Worker (PID: {worker_process.pid})")
    print(f"   - Celery Beat (PID: {beat_process.pid})")
    print("\n🎯 Les rappels programmés seront maintenant envoyés automatiquement!")
    print("⏰ Vérification toutes les minutes")
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
