#!/usr/bin/env python
"""
Test des APIs Super Admin avec authentification
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.test import APIClient
from events.models import UserProfile

def test_apis_with_auth():
    """Tester les APIs avec authentification"""
    print("🧪 Test des APIs Super Admin avec authentification...")
    
    # Créer un client API
    client = APIClient()
    
    # 1. Se connecter en tant que Super Admin
    print("\n🔐 Authentification...")
    try:
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"   ✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # Authentifier le client
        client.force_authenticate(user=super_admin)
        print("   ✅ Client authentifié")
        
    except Exception as e:
        print(f"   ❌ Erreur d'authentification: {e}")
        return
    
    # 2. Tester l'API des statistiques globales
    print("\n📊 Test API Statistiques Globales...")
    try:
        response = client.get('/api/admin/global_stats/')
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne - {len(data)} champs retournés")
            print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
            print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
            print(f"   📝 Total inscriptions: {data.get('total_registrations', 'N/A')}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.data}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 3. Tester l'API des utilisateurs
    print("\n👥 Test API Liste des Utilisateurs...")
    try:
        response = client.get('/api/admin/users/')
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne - {data.get('count', 0)} utilisateurs trouvés")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.data}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 4. Tester l'API des catégories
    print("\n📂 Test API Catégories...")
    try:
        response = client.get('/api/categories_management/')
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne - {len(data)} catégories trouvées")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.data}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 5. Tester l'API des tags
    print("\n🏷️  Test API Tags...")
    try:
        response = client.get('/api/tags_management/')
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne - {len(data)} tags trouvés")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.data}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 6. Tester l'API Analytics
    print("\n📈 Test API Analytics...")
    try:
        response = client.get('/api/admin/analytics_advanced/?period=month')
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne")
            if 'summary' in data:
                summary = data['summary']
                print(f"      👥 Total utilisateurs: {summary.get('total_platform_users', 'N/A')}")
                print(f"      🎪 Événements publiés: {summary.get('published_events', 'N/A')}")
                print(f"      💰 Revenus ce mois: {summary.get('this_month_revenue', 'N/A')}€")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.data}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 7. Tester l'API des remboursements
    print("\n💰 Test API Remboursements...")
    try:
        response = client.get('/api/refunds/')
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne - {data.get('count', 0)} remboursements trouvés")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.data}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_apis_with_auth()
