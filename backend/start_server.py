#!/usr/bin/env python
"""
Script de démarrage du serveur Django pour les tests
"""
import os
import sys
import django
import subprocess
import time

def start_django_server():
    """Démarre le serveur Django"""
    print("🚀 Démarrage du serveur Django...")
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings_minimal')
    
    try:
        django.setup()
        print("✅ Django configuré avec succès")
        
        # Démarrer le serveur
        print("🌐 Démarrage du serveur sur http://localhost:8000")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Lancer le serveur
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '--noreload'
        ])
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_django_server()
