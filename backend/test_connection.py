#!/usr/bin/env python
"""
Script de test pour vérifier la connexion frontend-backend
"""
import requests
import json

def test_backend_connection():
    """Tester la connexion au backend"""
    print("🔍 Test de connexion au backend...")
    
    # URL du backend sur Render
    backend_url = "https://event-management-backend-7uux.onrender.com"
    
    try:
        # Test 1: Vérifier que le backend répond
        print("\n1️⃣ Test de disponibilité du backend...")
        response = requests.get(f"{backend_url}/api/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Backend accessible")
        else:
            print(f"   ❌ Backend inaccessible: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return False
    
    try:
        # Test 2: Tester l'endpoint des événements
        print("\n2️⃣ Test de l'endpoint /events/...")
        response = requests.get(f"{backend_url}/api/events/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Événements récupérés: {len(data.get('results', []))} événements")
        else:
            print(f"   ❌ Erreur événements: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erreur événements: {e}")
    
    try:
        # Test 3: Tester l'authentification
        print("\n3️⃣ Test de l'authentification...")
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{backend_url}/api/auth/token/", json=auth_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Authentification réussie")
            
            # Test avec le token
            headers = {'Authorization': f'Bearer {token_data["access"]}'}
            response = requests.get(f"{backend_url}/api/events/", headers=headers, timeout=10)
            print(f"   Status avec token: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ API accessible avec authentification")
            else:
                print(f"   ❌ Erreur API avec token: {response.text[:200]}")
        else:
            print(f"   ❌ Erreur authentification: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erreur authentification: {e}")
    
    print("\n🎯 Test terminé !")
    return True

def test_cors_headers():
    """Tester les en-têtes CORS"""
    print("\n🌐 Test des en-têtes CORS...")
    
    backend_url = "https://event-management-backend-7uux.onrender.com"
    frontend_origin = "https://event-management-system-three-bay.vercel.app"
    
    try:
        headers = {
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(f"{backend_url}/api/events/", headers=headers, timeout=10)
        print(f"   Status OPTIONS: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print(f"   CORS Headers: {cors_headers}")
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("   ✅ CORS configuré")
        else:
            print("   ❌ CORS non configuré")
            
    except Exception as e:
        print(f"   ❌ Erreur CORS: {e}")

if __name__ == "__main__":
    print("🚀 Test de connexion frontend-backend")
    print("=" * 50)
    
    test_backend_connection()
    test_cors_headers()
