#!/usr/bin/env python
"""
🔐 SCRIPT DE TEST DE CONNEXION ADMIN
Teste la connexion admin sur Render
"""

import os
import sys
import django
import requests
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

def setup_django():
    """Configurer Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings_render')
    django.setup()

def test_admin_connection():
    """Tester la connexion admin"""
    print("🔐 TEST DE CONNEXION ADMIN")
    print("=" * 50)
    
    try:
        # Vérifier les utilisateurs admin
        print("👥 Vérification des utilisateurs admin...")
        User = get_user_model()
        admin_users = User.objects.filter(is_superuser=True)
        
        if admin_users.exists():
            print(f"✅ {admin_users.count()} superutilisateur(s) trouvé(s):")
            for user in admin_users:
                print(f"   - {user.username} ({user.email})")
        else:
            print("❌ Aucun superutilisateur trouvé")
            return False
        
        # Tester l'API d'authentification
        print("\n🔑 Test de l'API d'authentification...")
        backend_url = "https://event-management-backend-7uux.onrender.com"
        
        # Test de l'endpoint de login
        login_url = f"{backend_url}/api/auth/login/"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(login_url, json=login_data, timeout=10)
            if response.status_code == 200:
                print("✅ API d'authentification fonctionnelle")
                token_data = response.json()
                print(f"   - Token reçu: {token_data.get('access', 'N/A')[:20]}...")
            else:
                print(f"❌ Erreur API d'authentification: {response.status_code}")
                print(f"   - Réponse: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion à l'API: {e}")
            return False
        
        # Tester l'endpoint admin
        print("\n🛡️ Test de l'interface admin...")
        admin_url = f"{backend_url}/admin/"
        try:
            response = requests.get(admin_url, timeout=10)
            if response.status_code == 200:
                print("✅ Interface admin accessible")
            else:
                print(f"❌ Interface admin non accessible: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion à l'admin: {e}")
        
        # Tester l'API des événements
        print("\n📅 Test de l'API des événements...")
        events_url = f"{backend_url}/api/events/"
        try:
            response = requests.get(events_url, timeout=10)
            if response.status_code == 200:
                print("✅ API des événements fonctionnelle")
                events_data = response.json()
                print(f"   - {len(events_data)} événement(s) trouvé(s)")
            else:
                print(f"❌ Erreur API des événements: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion à l'API des événements: {e}")
        
        print("\n🎉 TESTS TERMINÉS!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def main():
    """Fonction principale"""
    setup_django()
    success = test_admin_connection()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
