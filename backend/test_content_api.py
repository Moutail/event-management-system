#!/usr/bin/env python
"""
Test de l'API de génération de contenu
"""

import requests
import json

def test_content_api():
    """Test de l'API de génération de contenu"""
    print("🎨 Test de l'API de génération de contenu")
    print("=" * 50)
    
    # URL de base
    base_url = "http://localhost:8001/api"
    
    # Test 1: Génération de contenu pour un workshop
    print("\n🔍 Test 1: Génération de contenu pour un workshop")
    try:
        url = f"{base_url}/admin/generate_content/"
        payload = {
            'title': 'Workshop Innovation Tech',
            'category': 'Workshop',
            'location': 'Paris',
            'price': 50.0,
            'max_capacity': 25
        }
        
        print(f"   URL: {url}")
        print(f"   Payload: {payload}")
        
        response = requests.post(url, json=payload)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Succès!")
            print(f"   Description: {data['generated_content']['description'][:100]}...")
            print(f"   Hashtags: {data['generated_content']['hashtags']}")
            print(f"   Couleurs: {data['generated_content']['visual_suggestions']['colors'][:3]}")
            print(f"   Style: {data['generated_content']['visual_suggestions']['style']}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Génération de contenu pour un concert
    print("\n🔍 Test 2: Génération de contenu pour un concert")
    try:
        payload = {
            'title': 'Festival de Musique Électronique',
            'category': 'Concert',
            'location': 'Montreal',
            'price': 45.0,
            'max_capacity': 500
        }
        
        print(f"   Payload: {payload}")
        
        response = requests.post(url, json=payload)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Succès!")
            print(f"   Description: {data['generated_content']['description'][:100]}...")
            print(f"   Hashtags: {data['generated_content']['hashtags']}")
            print(f"   Couleurs: {data['generated_content']['visual_suggestions']['colors'][:3]}")
            print(f"   Style: {data['generated_content']['visual_suggestions']['style']}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 3: Génération de contenu pour un meetup gratuit
    print("\n🔍 Test 3: Génération de contenu pour un meetup gratuit")
    try:
        payload = {
            'title': 'Meetup Développeurs Web',
            'category': 'Meetup',
            'location': 'Lyon',
            'price': 0,
            'max_capacity': 50
        }
        
        print(f"   Payload: {payload}")
        
        response = requests.post(url, json=payload)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Succès!")
            print(f"   Description: {data['generated_content']['description'][:100]}...")
            print(f"   Hashtags: {data['generated_content']['hashtags']}")
            print(f"   Couleurs: {data['generated_content']['visual_suggestions']['colors'][:3]}")
            print(f"   Style: {data['generated_content']['visual_suggestions']['style']}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 4: Test d'erreur - données manquantes
    print("\n🔍 Test 4: Test d'erreur - données manquantes")
    try:
        payload = {
            'title': 'Test Incomplet',
            # Catégorie manquante
            'location': 'Paris'
        }
        
        print(f"   Payload: {payload}")
        
        response = requests.post(url, json=payload)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            print("   ✅ Erreur attendue - validation des données")
            print(f"   Message: {response.json().get('error', 'Erreur de validation')}")
        else:
            print(f"   ⚠️ Status inattendu: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n✅ Test terminé!")

if __name__ == '__main__':
    test_content_api()
















