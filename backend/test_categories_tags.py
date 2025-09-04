#!/usr/bin/env python3
"""
🧪 TEST SIMPLE DES APIS CATÉGORIES ET TAGS
"""

import requests
import json

def test_categories_tags_apis():
    """Test des APIs de gestion des catégories et tags"""
    
    base_url = "http://localhost:8001/api"
    
    # Headers pour l'authentification (à adapter selon ton token)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # Remplace par ton vrai token
    }
    
    print("🧪 TEST DES APIS CATÉGORIES ET TAGS")
    print("=" * 50)
    
    # Test 1: Récupération des catégories
    print("\n1️⃣ Test GET /categories_management/")
    try:
        response = requests.get(f"{base_url}/categories_management/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test 2: Récupération des tags
    print("\n2️⃣ Test GET /tags_management/")
    try:
        response = requests.get(f"{base_url}/tags_management/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test 3: Création d'une catégorie de test
    print("\n3️⃣ Test POST /categories_management/")
    category_data = {
        "name": "Test Category",
        "description": "Catégorie de test",
        "color": "#FF0000",
        "icon": "🎯"
    }
    try:
        response = requests.post(
            f"{base_url}/categories_management/", 
            headers=headers,
            json=category_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}...")
        
        if response.status_code == 201:
            category_id = response.json().get('id')
            print(f"   ✅ Catégorie créée avec ID: {category_id}")
            
            # Test 4: Modification de la catégorie
            print("\n4️⃣ Test PUT /categories_management/{id}/")
            update_data = {"name": "Test Category Updated"}
            response = requests.put(
                f"{base_url}/categories_management/{category_id}/",
                headers=headers,
                json=update_data
            )
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            
            # Test 5: Suppression de la catégorie
            print("\n5️⃣ Test DELETE /categories_management/{id}/")
            response = requests.delete(
                f"{base_url}/categories_management/{category_id}/",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    print("\n🎯 Tests terminés!")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Assure-toi que:")
    print("   1. Le serveur Django tourne sur le port 8001")
    print("   2. Tu as un token d'authentification valide")
    print("   3. Tu es connecté en tant que Super Admin")
    print("\n   Remplace 'YOUR_TOKEN_HERE' par ton vrai token JWT")
    print("=" * 50)
    
    test_categories_tags_apis()














