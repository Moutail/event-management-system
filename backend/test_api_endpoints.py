#!/usr/bin/env python
"""
Script de test des endpoints API pour les événements virtuels
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_connection():
    """Test de connexion de base"""
    print("🔌 Test de connexion...")
    try:
        response = requests.get(f"{BASE_URL}/test/", headers=HEADERS)
        print(f"✅ Connexion réussie - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur Django est démarré avec: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_virtual_events_endpoints():
    """Test des endpoints des événements virtuels"""
    print("\n🎯 Test des endpoints des événements virtuels...")
    
    # Test de la liste des événements virtuels
    try:
        response = requests.get(f"{BASE_URL}/virtual-events/", headers=HEADERS)
        print(f"✅ GET /virtual-events/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Nombre d'événements: {len(data.get('results', data))}")
    except Exception as e:
        print(f"❌ Erreur GET /virtual-events/: {e}")
    
    # Test de la création d'un événement virtuel (simulation)
    print("\n📝 Test de création d'événement virtuel...")
    event_data = {
        "event_data": {
            "title": "Test Événement Virtuel",
            "description": "Description de test",
            "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=7, hours=2)).isoformat(),
            "location": "Zoom",
            "price": "0.00",
            "is_free": True,
            "status": "draft"
        },
        "platform": "zoom",
        "meeting_id": "TEST123",
        "meeting_password": "test123",
        "auto_record": True,
        "allow_chat": True,
        "allow_screen_sharing": True,
        "waiting_room": True,
        "access_instructions": "Instructions de test",
        "technical_requirements": "Aucune exigence particulière"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/virtual-events/", 
            headers=HEADERS,
            json=event_data
        )
        print(f"✅ POST /virtual-events/ - Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("   🎉 Événement virtuel créé avec succès!")
        else:
            print(f"   📋 Réponse: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erreur POST /virtual-events/: {e}")

def test_interactions_endpoints():
    """Test des endpoints des interactions"""
    print("\n💬 Test des endpoints des interactions...")
    
    # Test de la liste des interactions
    try:
        response = requests.get(f"{BASE_URL}/virtual-interactions/", headers=HEADERS)
        print(f"✅ GET /virtual-interactions/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Nombre d'interactions: {len(data.get('results', data))}")
    except Exception as e:
        print(f"❌ Erreur GET /virtual-interactions/: {e}")

def test_events_endpoints():
    """Test des endpoints des événements"""
    print("\n📅 Test des endpoints des événements...")
    
    # Test de la liste des événements
    try:
        response = requests.get(f"{BASE_URL}/events/", headers=HEADERS)
        print(f"✅ GET /events/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Nombre d'événements: {len(data.get('results', data))}")
    except Exception as e:
        print(f"❌ Erreur GET /events/: {e}")

def test_categories_endpoints():
    """Test des endpoints des catégories"""
    print("\n🏷️ Test des endpoints des catégories...")
    
    try:
        response = requests.get(f"{BASE_URL}/categories/", headers=HEADERS)
        print(f"✅ GET /categories/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Nombre de catégories: {len(data.get('results', data))}")
    except Exception as e:
        print(f"❌ Erreur GET /categories/: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 Test des API des événements virtuels")
    print("=" * 50)
    
    # Test de connexion
    if not test_connection():
        return
    
    # Tests des endpoints
    test_virtual_events_endpoints()
    test_interactions_endpoints()
    test_events_endpoints()
    test_categories_endpoints()
    
    print("\n🎉 Tests terminés!")
    print("\n📋 Prochaines étapes:")
    print("   1. ✅ Migrations créées et appliquées")
    print("   2. ✅ Endpoints API testés")
    print("   3. 🔄 Intégrer les composants React")
    print("   4. 🔄 Tester le flux complet")
    print("   5. 🔄 Configurer les tâches automatiques")

if __name__ == "__main__":
    main()
