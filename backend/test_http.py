#!/usr/bin/env python
"""
Test HTTP simple des APIs Super Admin
"""
import requests
import json

def test_apis():
    """Tester les APIs via HTTP"""
    print("🧪 Test HTTP des APIs Super Admin...")
    
    base_url = "http://localhost:8000/api"
    
    # 1. Tester l'API des statistiques globales
    print("\n📊 Test API Statistiques Globales...")
    try:
        response = requests.get(f"{base_url}/admin/global_stats/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne - {len(data)} champs retournés")
            print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
            print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
        elif response.status_code == 401:
            print("   🔒 Authentification requise (normal)")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
    
    # 2. Tester l'API Analytics
    print("\n📈 Test API Analytics...")
    try:
        response = requests.get(f"{base_url}/admin/analytics_advanced/?period=month")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne")
        elif response.status_code == 401:
            print("   🔒 Authentification requise (normal)")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
    
    # 3. Tester l'API des remboursements
    print("\n💰 Test API Remboursements...")
    try:
        response = requests.get(f"{base_url}/refunds/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API fonctionne")
        elif response.status_code == 401:
            print("   🔒 Authentification requise (normal)")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
    
    print("\n🎯 Test terminé!")
    print("   - Status 401 = Normal (authentification requise)")
    print("   - Status 200 = API fonctionne")
    print("   - Status 500 = Erreur serveur (à corriger)")

if __name__ == '__main__':
    test_apis()
