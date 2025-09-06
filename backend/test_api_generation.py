#!/usr/bin/env python
"""
Test de l'API de génération de contenu
"""

import requests
import json

def test_api_generation():
    """Test de l'API de génération de contenu"""
    print("🔍 Test de l'API de génération de contenu")
    print("=" * 50)
    
    # URL de l'API
    url = "http://localhost:8001/api/admin/generate_content/"
    
    # Données de test
    test_data = {
        "title": "Concert Rock 2024",
        "category": "Concert",
        "location": "Lyon",
        "price": 45.0,
        "max_capacity": 500
    }
    
    print(f"🎯 Test avec l'événement: {test_data['title']}")
    print(f"   Catégorie: {test_data['category']}")
    print(f"   Lieu: {test_data['location']}")
    print(f"   Prix: {test_data['price']}€")
    print(f"   Capacité: {test_data['max_capacity']} personnes")
    
    try:
        print("\n🔄 Envoi de la requête...")
        response = requests.post(url, json=test_data)
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération réussie !")
            print("\n📝 Contenu généré:")
            print(f"   Description: {result['generated_content']['description'][:100]}...")
            print(f"   Hashtags: {' '.join(result['generated_content']['hashtags'])}")
            print(f"   Suggestions visuelles: {len(result['generated_content']['visual_suggestions'])} éléments")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur Django est démarré sur le port 8001")
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")

if __name__ == "__main__":
    test_api_generation()
















