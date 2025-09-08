#!/usr/bin/env python
"""
Test de l'endpoint API de l'IA de prédiction
"""

import requests
import json

def test_api_ia():
    """Test de l'endpoint API"""
    print("🧪 Test de l'endpoint API de l'IA de prédiction")
    print("=" * 50)
    
    # URL de base
    base_url = "http://localhost:8001/api"
    
    # Test 1: Analytics prédictifs globaux
    print("\n🔍 Test 1: Analytics prédictifs globaux")
    try:
        url = f"{base_url}/admin/predictive_analytics/?days_back=90"
        print(f"   URL: {url}")
        
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Succès!")
            print(f"   Insights: {len(data.get('insights', {}).get('global_insights', []))}")
            print(f"   Tendances: {len(data.get('trends', {}).get('emerging_trends', []))}")
            print(f"   Modèles: {data.get('model_status', {})}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Analytics pour un événement spécifique
    print("\n🔍 Test 2: Analytics pour un événement spécifique")
    try:
        # D'abord récupérer la liste des événements
        events_url = f"{base_url}/events/"
        events_response = requests.get(events_url)
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            if events_data.get('results') and len(events_data['results']) > 0:
                event_id = events_data['results'][0]['id']
                print(f"   Événement testé: ID {event_id}")
                
                url = f"{base_url}/admin/predictive_analytics/?event_id={event_id}&days_back=90"
                print(f"   URL: {url}")
                
                response = requests.get(url)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("   ✅ Succès!")
                    print(f"   Insights spécifiques: {len(data.get('insights', {}).get('event_specific_insights', []))}")
                else:
                    print(f"   ❌ Erreur: {response.text}")
            else:
                print("   ⚠️ Aucun événement disponible pour le test")
        else:
            print(f"   ❌ Erreur lors de la récupération des événements: {events_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n✅ Test terminé!")

if __name__ == '__main__':
    test_api_ia()

















