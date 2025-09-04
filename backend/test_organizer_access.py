#!/usr/bin/env python
"""
Test de l'accès des organisateurs à l'API de génération de contenu
"""

import requests
import json

def test_organizer_access():
    """Test de l'accès des organisateurs à l'API"""
    print("🔍 Test de l'accès des organisateurs à l'API de génération de contenu")
    print("=" * 70)
    
    # URL de l'API
    url = "http://localhost:8001/api/admin/generate_content/"
    
    # Données de test
    test_data = {
        "title": "Test Organisateur Access",
        "category": "Workshop",
        "location": "Paris",
        "price": 25.0,
        "max_capacity": 20
    }
    
    print(f"🎯 Test avec l'événement: {test_data['title']}")
    print(f"   Catégorie: {test_data['category']}")
    print(f"   Lieu: {test_data['location']}")
    print(f"   Prix: {test_data['price']}€")
    print(f"   Capacité: {test_data['max_capacity']} personnes")
    
    print("\n⚠️  NOTE: Ce test nécessite que l'utilisateur soit connecté")
    print("   Connectez-vous d'abord avec un compte organisateur dans l'interface")
    print("   Puis copiez le token d'authentification")
    
    # Demander le token
    token = input("\n🔑 Entrez le token d'authentification (ou appuyez sur Entrée pour tester sans token): ").strip()
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        print(f"   Token fourni: {'*' * 20}...{token[-8:]}")
    else:
        print("   Aucun token fourni - test sans authentification")
    
    try:
        print("\n🔄 Envoi de la requête...")
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération réussie !")
            print("\n📝 Contenu généré:")
            print(f"   Description: {result['generated_content']['description'][:100]}...")
            print(f"   Hashtags: {' '.join(result['generated_content']['hashtags'])}")
            print(f"   Suggestions visuelles: {len(result['generated_content']['visual_suggestions'])} éléments")
            
            print("\n🎉 L'API fonctionne maintenant pour les organisateurs !")
            
        elif response.status_code == 401:
            print("❌ Non authentifié (401)")
            print("   Connectez-vous d'abord avec un compte organisateur")
            
        elif response.status_code == 403:
            print("❌ Accès refusé (403)")
            print("   L'utilisateur n'a pas les bonnes permissions")
            print("   Vérifiez que c'est un organisateur ou super admin")
            
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur Django est démarré sur le port 8001")
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")

if __name__ == '__main__':
    test_organizer_access()
