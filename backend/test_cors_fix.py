#!/usr/bin/env python
"""
Script de test pour vérifier la correction CORS
"""
import requests
import json

def test_cors_fix():
    """Tester la correction CORS"""
    print("🔍 Test de la correction CORS...")
    
    backend_url = "https://event-management-backend-7uux.onrender.com"
    frontend_origin = "https://event-management-system-git-main-moutails-projects.vercel.app"
    
    # Test 1: Vérifier que le backend répond
    print("\n1️⃣ Test de disponibilité du backend...")
    try:
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
    
    # Test 2: Test CORS avec le nouveau domaine
    print("\n2️⃣ Test CORS avec le nouveau domaine Vercel...")
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
            print("   ✅ CORS configuré correctement")
        else:
            print("   ❌ CORS non configuré")
            
    except Exception as e:
        print(f"   ❌ Erreur CORS: {e}")
    
    # Test 3: Test de l'API avec le nouveau domaine
    print("\n3️⃣ Test de l'API avec le nouveau domaine...")
    try:
        headers = {
            'Origin': frontend_origin,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{backend_url}/api/events/", headers=headers, timeout=10)
        print(f"   Status GET: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API accessible: {len(data.get('results', []))} événements")
        else:
            print(f"   ❌ Erreur API: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erreur API: {e}")
    
    # Test 4: Test d'authentification
    print("\n4️⃣ Test d'authentification...")
    try:
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        headers = {
            'Origin': frontend_origin,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f"{backend_url}/api/auth/token/", json=auth_data, headers=headers, timeout=10)
        print(f"   Status AUTH: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Authentification réussie")
            print(f"   Token reçu: {token_data.get('access', 'N/A')[:20]}...")
        else:
            print(f"   ❌ Erreur authentification: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erreur authentification: {e}")
    
    print("\n🎯 Test terminé !")
    return True

if __name__ == "__main__":
    test_cors_fix()
