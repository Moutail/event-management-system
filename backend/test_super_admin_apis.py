#!/usr/bin/env python
"""
Script de test pour vérifier les APIs Super Admin
"""
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def test_super_admin_apis():
    """Tester toutes les APIs Super Admin"""
    print("🧪 Test des APIs Super Admin...")
    
    # URL de base
    base_url = "http://localhost:8000/api"
    
    # 1. Vérifier que le Super Admin existe
    try:
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
        return
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
        return
    
    # 2. Tester l'API des statistiques globales
    print("\n📊 Test API Statistiques Globales...")
    try:
        response = requests.get(f"{base_url}/admin/global_stats/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne - {len(data)} champs retournés")
            print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
            print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
            print(f"   📝 Total inscriptions: {data.get('total_registrations', 'N/A')}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 3. Tester l'API des utilisateurs
    print("\n👥 Test API Liste des Utilisateurs...")
    try:
        response = requests.get(f"{base_url}/admin/users/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne - {data.get('count', 0)} utilisateurs trouvés")
            if data.get('results'):
                for user in data['results'][:3]:  # Afficher les 3 premiers
                    print(f"      👤 {user.get('username')} ({user.get('role')}) - {user.get('status')}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 4. Tester l'API des catégories
    print("\n📂 Test API Catégories...")
    try:
        response = requests.get(f"{base_url}/categories_management/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne - {len(data)} catégories trouvées")
            for cat in data[:3]:
                print(f"      🏷️  {cat.get('name')} - {cat.get('description', 'N/A')}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 5. Tester l'API des tags
    print("\n🏷️  Test API Tags...")
    try:
        response = requests.get(f"{base_url}/tags_management/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne - {len(data)} tags trouvés")
            for tag in data[:3]:
                print(f"      🏷️  {tag.get('name')} - {tag.get('color')}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 6. Tester l'API Analytics
    print("\n📈 Test API Analytics...")
    try:
        response = requests.get(f"{base_url}/admin/analytics_advanced/?period=month")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne")
            if 'summary' in data:
                summary = data['summary']
                print(f"      👥 Total utilisateurs: {summary.get('total_platform_users', 'N/A')}")
                print(f"      🎪 Événements publiés: {summary.get('published_events', 'N/A')}")
                print(f"      💰 Revenus ce mois: {summary.get('this_month_revenue', 'N/A')}€")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Résumé des tests:")
    print("   - Vérifiez que le serveur Django est démarré sur le port 8000")
    print("   - Vérifiez que les données de test ont été créées")
    print("   - Testez le frontend en vous connectant en tant que Super Admin")

if __name__ == '__main__':
    test_super_admin_apis()
