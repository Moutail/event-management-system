#!/usr/bin/env python
"""
🚀 DÉMARRAGE DES SERVICES DE PRODUCTION
Script pour démarrer tous les services nécessaires en production
"""

import os
import sys
import subprocess
import time
import signal
from multiprocessing import Process

def start_web_server():
    """Démarrer le serveur web Django avec Gunicorn"""
    print("🌐 Démarrage du serveur web...")
    try:
        subprocess.run([
            'gunicorn', 'event_management.wsgi:application',
            '--bind', '0.0.0.0:8000',
            '--workers', '3',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload'
        ])
    except Exception as e:
        print(f"❌ Erreur serveur web: {e}")

def start_celery_worker():
    """Démarrer le worker Celery"""
    print("👷 Démarrage du worker Celery...")
    try:
        subprocess.run([
            'celery', '-A', 'event_management', 'worker',
            '--loglevel=info',
            '--concurrency=2',
            '--max-tasks-per-child=1000'
        ])
    except Exception as e:
        print(f"❌ Erreur worker Celery: {e}")

def start_celery_beat():
    """Démarrer le scheduler Celery Beat"""
    print("⏰ Démarrage du scheduler Celery Beat...")
    try:
        subprocess.run([
            'celery', '-A', 'event_management', 'beat',
            '--loglevel=info',
            '--schedule=celerybeat-schedule'
        ])
    except Exception as e:
        print(f"❌ Erreur Celery Beat: {e}")

def start_notification_service():
    """Démarrer le service de notifications automatiques"""
    print("📧 Démarrage du service de notifications...")
    try:
        while True:
            try:
                # Exécuter la commande de notifications
                result = subprocess.run([
                    'python', 'manage.py', 'send_event_notifications'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"✅ Notifications envoyées: {result.stdout}")
                else:
                    print(f"⚠️ Erreur notifications: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout lors de l'envoi des notifications")
            except Exception as e:
                print(f"❌ Erreur service notifications: {e}")
            
            # Attendre 15 minutes avant la prochaine exécution
            print("⏳ Attente de 15 minutes...")
            time.sleep(900)  # 15 minutes
            
    except KeyboardInterrupt:
        print("🛑 Service de notifications arrêté")

def signal_handler(signum, frame):
    """Gestionnaire de signal pour l'arrêt propre"""
    print("\n🛑 Arrêt des services...")
    sys.exit(0)

def main():
    """Fonction principale"""
    print("🎯 DÉMARRAGE DES SERVICES DE PRODUCTION")
    print("=" * 60)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('manage.py'):
        print("❌ Erreur: manage.py non trouvé. Assurez-vous d'être dans le dossier backend.")
        return False
    
    # Configuration des signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrer les services en parallèle
    processes = []
    
    try:
        # Service web (principal)
        web_process = Process(target=start_web_server)
        web_process.start()
        processes.append(web_process)
        
        # Worker Celery
        worker_process = Process(target=start_celery_worker)
        worker_process.start()
        processes.append(worker_process)
        
        # Celery Beat
        beat_process = Process(target=start_celery_beat)
        beat_process.start()
        processes.append(beat_process)
        
        # Service de notifications
        notification_process = Process(target=start_notification_service)
        notification_process.start()
        processes.append(notification_process)
        
        print("\n" + "=" * 60)
        print("🎉 TOUS LES SERVICES DÉMARRÉS!")
        print("=" * 60)
        print("📋 Services actifs:")
        print(f"   - Serveur web (PID: {web_process.pid})")
        print(f"   - Worker Celery (PID: {worker_process.pid})")
        print(f"   - Celery Beat (PID: {beat_process.pid})")
        print(f"   - Service notifications (PID: {notification_process.pid})")
        print("\n💡 Pour arrêter: Ctrl+C")
        print("=" * 60)
        
        # Attendre que tous les processus se terminent
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt des services...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
        print("✅ Services arrêtés")
        return True
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        sys.exit(1)
