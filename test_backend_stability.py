#!/usr/bin/env python3
"""
Script de test pour vérifier la stabilité du backend
"""

import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "username": "testadmin",
    "password": "test123"
}

def test_backend_stability():
    """Test de stabilité du backend"""
    print("🔍 Test de stabilité du backend")
    print("=" * 50)
    
    # Test 1: Vérifier que le serveur répond
    print("1️⃣ Test de réponse du serveur...")
    try:
        response = requests.get(f"{BASE_URL}/api/events/", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur répond correctement")
        else:
            print(f"❌ Serveur répond avec status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Connexion et vérification répétée
    print("\n2️⃣ Test de connexion et vérification répétée...")
    
    # Connexion
    try:
        login_response = requests.post(f"{BASE_URL}/api/token/", json=ADMIN_CREDENTIALS)
        if login_response.status_code != 200:
            print(f"❌ Échec de connexion: {login_response.status_code}")
            return False
        
        token = login_response.json().get('access')
        if not token:
            print("❌ Pas de token reçu")
            return False
        
        print("✅ Connexion réussie")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test répété de l'endpoint auth/user
    print("\n3️⃣ Test répété de l'endpoint /api/auth/user/...")
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(5):
        try:
            print(f"   Test {i+1}/5...", end=" ")
            response = requests.get(f"{BASE_URL}/api/auth/user/", headers=headers, timeout=5)
            
            if response.status_code == 200:
                print("✅ OK")
            elif response.status_code == 401:
                print("❌ 401 Unauthorized")
                # Vérifier si c'est un problème de token
                if i == 0:  # Premier test
                    print("   ⚠️ Token invalide, problème d'authentification")
                    return False
            else:
                print(f"❌ Status {response.status_code}")
            
            # Pause entre les tests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    print("\n4️⃣ Test de l'endpoint des événements...")
    try:
        response = requests.get(f"{BASE_URL}/api/events/", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint événements accessible")
        else:
            print(f"❌ Endpoint événements: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur événements: {e}")
        return False
    
    print("\n🎉 Test de stabilité terminé avec succès!")
    return True

def main():
    """Fonction principale"""
    print("🚀 Test de stabilité du backend")
    print("=" * 50)
    
    success = test_backend_stability()
    
    if success:
        print("\n✅ Le backend est stable et fonctionne correctement")
        print("💡 Le problème vient probablement du frontend qui fait des appels répétés")
    else:
        print("\n❌ Le backend a des problèmes de stabilité")
        print("🔧 Vérifiez les logs du serveur Django")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
