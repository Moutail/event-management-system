#!/usr/bin/env python
"""
Test de l'API des événements
"""

import requests
import json

def test_events_api():
    """Test de l'API des événements"""
    print("🧪 Test de l'API des événements")
    print("=" * 40)
    
    # URL de base
    base_url = "http://localhost:8001/api"
    
    # Test 1: Récupération des événements
    print("\n🔍 Test 1: Récupération des événements")
    try:
        url = f"{base_url}/events/"
        print(f"   URL: {url}")
        
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Succès!")
            print(f"   Type de données reçues: {type(data)}")
            print(f"   Contenu brut: {data[:100] if isinstance(data, list) else str(data)[:100]}")
            
            # Gérer le cas où l'API retourne une liste directement
            if isinstance(data, list):
                events = data
                print(f"   Total d'événements: {len(events)}")
            else:
                events = data.get('results', [])
                print(f"   Total d'événements: {data.get('count', 'N/A')}")
                print(f"   Événements dans cette page: {len(events)}")
            
            if events:
                print("\n   📋 Premiers événements:")
                for i, event in enumerate(events[:3]):
                    print(f"      {i+1}. {event.get('title', 'Sans titre')}")
                    print(f"         ID: {event.get('id')}")
                    print(f"         Lieu: {event.get('location', 'Non spécifié')}")
                    print(f"         Catégorie: {event.get('category', {}).get('name', 'Aucune')}")
                    print(f"         Statut: {event.get('status', 'Inconnu')}")
                    print()
            else:
                print("   ⚠️ Aucun événement trouvé")
                
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Recherche d'événements
    print("\n🔍 Test 2: Recherche d'événements")
    try:
        search_terms = ['WINNER', 'TEST', 'Conférence']
        
        for term in search_terms:
            url = f"{base_url}/events/?search={term}"
            print(f"   Recherche '{term}': {url}")
            
            response = requests.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"   ✅ Résultats: {len(results)} événements trouvés")
                
                if results:
                    for event in results:
                        print(f"      - {event.get('title')} (ID: {event.get('id')})")
                else:
                    print(f"      ⚠️ Aucun résultat pour '{term}'")
            else:
                print(f"   ❌ Erreur: {response.text}")
            
            print()
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n✅ Test terminé!")

if __name__ == '__main__':
    test_events_api()
