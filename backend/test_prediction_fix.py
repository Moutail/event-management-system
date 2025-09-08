#!/usr/bin/env python
"""
Test de la correction de la prédiction
"""

import requests
import json

def test_prediction_fix():
    """Test de la correction de la prédiction"""
    print("🧪 Test de la correction de la prédiction")
    print("=" * 50)
    
    # URL de base
    base_url = "http://localhost:8001/api"
    
    # Test 1: Prédiction du taux de remplissage
    print("\n🔍 Test 1: Prédiction du taux de remplissage")
    try:
        # D'abord récupérer la liste des événements
        events_url = f"{base_url}/events/"
        events_response = requests.get(events_url)
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            if events_data and len(events_data) > 0:
                # Prendre le premier événement
                event = events_data[0]
                event_id = event['id']
                event_title = event['title']
                
                print(f"   🎯 Test avec l'événement: {event_title} (ID: {event_id})")
                
                # Tester la prédiction
                url = f"{base_url}/admin/predict_fill_rate/"
                payload = {
                    'event_id': event_id
                }
                
                print(f"   URL: {url}")
                print(f"   Payload: {payload}")
                
                response = requests.post(url, json=payload)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("   ✅ Succès!")
                    print(f"   Réponse: {json.dumps(data, indent=2)}")
                    
                    # Vérifier la structure de la réponse
                    if 'status' in data and data['status'] == 'success':
                        print("   ✅ Structure de réponse correcte")
                        if 'prediction' in data:
                            prediction = data['prediction']
                            if 'status' in prediction:
                                print(f"   ✅ Prédiction: {prediction['status']}")
                                if prediction['status'] == 'success':
                                    print(f"   🎯 Taux de remplissage prédit: {prediction.get('prediction', 'N/A')}")
                                    print(f"   🎯 Confiance: {prediction.get('confidence', 'N/A')}")
                                else:
                                    print(f"   ⚠️ Erreur dans la prédiction: {prediction.get('message', 'N/A')}")
                            else:
                                print("   ⚠️ Pas de statut dans la prédiction")
                        else:
                            print("   ⚠️ Pas de prédiction dans la réponse")
                    else:
                        print("   ⚠️ Statut de réponse incorrect")
                        
                else:
                    print(f"   ❌ Erreur: {response.text}")
                    
            else:
                print("   ⚠️ Aucun événement disponible pour le test")
        else:
            print(f"   ❌ Erreur lors de la récupération des événements: {events_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Optimisation des prix
    print("\n🔍 Test 2: Optimisation des prix")
    try:
        if 'event_id' in locals():
            url = f"{base_url}/admin/optimize_pricing/"
            payload = {
                'event_id': event_id,
                'target_fill_rate': 0.8
            }
            
            print(f"   URL: {url}")
            print(f"   Payload: {payload}")
            
            response = requests.post(url, json=payload)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Succès!")
                print(f"   Réponse: {json.dumps(data, indent=2)}")
            else:
                print(f"   ❌ Erreur: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n✅ Test terminé!")

if __name__ == '__main__':
    test_prediction_fix()

















