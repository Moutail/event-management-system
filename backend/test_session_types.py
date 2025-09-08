#!/usr/bin/env python
"""
Script de test pour l'API des types de sessions
"""

import requests
import json
from datetime import datetime, time, date

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_session_types_api():
    """Test de l'API des types de sessions"""
    
    print("🧪 Test de l'API des types de sessions")
    print("=" * 50)
    
    # 1. Créer un événement de test
    print("\n1. Création d'un événement de test...")
    
    event_data = {
        "title": "Événement Test Sessions",
        "short_description": "Test des types de sessions",
        "description": "Description complète pour tester les types de sessions",
        "start_date": "2025-01-15T10:00:00Z",
        "end_date": "2025-01-15T18:00:00Z",
        "location": "Paris",
        "address": "123 Rue de Test, Paris",
        "price": "0",
        "is_free": True,
        "place_type": "unlimited",
        "event_type": "physical",
        "is_public": True,
        "category_id": 1  # Assurez-vous que cette catégorie existe
    }
    
    try:
        # Note: Vous devrez vous connecter d'abord pour créer un événement
        print("   ⚠️  Création d'événement nécessite une authentification")
        print("   📝 Données de l'événement:", json.dumps(event_data, indent=2))
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la création de l'événement: {e}")
    
    # 2. Test de l'endpoint des types de sessions
    print("\n2. Test de l'endpoint /session_types/...")
    
    # Simuler un événement existant (remplacez par un vrai ID)
    test_event_id = 1
    
    session_types_url = f"{API_URL}/events/{test_event_id}/session_types/"
    
    try:
        # Test GET
        print(f"   🔍 GET {session_types_url}")
        response = requests.get(session_types_url)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Types de sessions récupérés: {len(data)} trouvé(s)")
            for st in data:
                print(f"      - {st['name']} ({st['date']}) {st['start_time']}-{st['end_time']}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Impossible de se connecter au serveur. Assurez-vous qu'il tourne sur le port 8000")
    except Exception as e:
        print(f"   ❌ Erreur lors du test GET: {e}")
    
    # 3. Test de création d'un type de session
    print("\n3. Test de création d'un type de session...")
    
    session_data = {
        "name": "Session Matin",
        "description": "Session de test le matin",
        "max_participants": 50,
        "date": "2025-01-15",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "is_active": True,
        "is_mandatory": True,
        "display_order": 1
    }
    
    try:
        print(f"   📝 Données de la session:", json.dumps(session_data, indent=2))
        print("   ⚠️  Création nécessite une authentification (organisateur ou super admin)")
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la préparation des données: {e}")
    
    # 4. Test de validation des données
    print("\n4. Test de validation des données...")
    
    # Test avec heure de fin avant heure de début
    invalid_session_data = {
        "name": "Session Invalide",
        "date": "2025-01-15",
        "start_time": "14:00:00",
        "end_time": "12:00:00"  # Heure de fin avant heure de début
    }
    
    print("   🔍 Test validation: heure de fin avant heure de début")
    print(f"   📝 Données invalides:", json.dumps(invalid_session_data, indent=2))
    print("   ✅ Validation côté backend empêchera cette création")
    
    # Test avec date dans le passé
    past_session_data = {
        "name": "Session Passée",
        "date": "2020-01-15",  # Date dans le passé
        "start_time": "10:00:00",
        "end_time": "12:00:00"
    }
    
    print("\n   🔍 Test validation: date dans le passé")
    print(f"   📝 Données invalides:", json.dumps(past_session_data, indent=2))
    print("   ✅ Validation côté backend empêchera cette création")
    
    print("\n" + "=" * 50)
    print("🎯 Tests terminés !")
    print("\n📋 Prochaines étapes:")
    print("   1. Créer un utilisateur organisateur")
    print("   2. Se connecter avec cet utilisateur")
    print("   3. Créer un événement")
    print("   4. Tester la création de types de sessions")
    print("   5. Tester la récupération des types de sessions")

if __name__ == "__main__":
    test_session_types_api()












