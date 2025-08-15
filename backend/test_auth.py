#!/usr/bin/env python
"""
Test de l'authentification et des permissions Super Admin
"""
import requests
import json

def test_auth():
    """Tester l'authentification"""
    print("🔐 Test de l'authentification Super Admin...")
    
    base_url = "http://localhost:8000/api"
    
    # 1. Test sans authentification (doit retourner 401)
    print("\n📊 Test sans authentification...")
    try:
        response = requests.get(f"{base_url}/admin/global_stats/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correct - Authentification requise")
        else:
            print(f"   ❌ Inattendu: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 2. Test avec un token invalide (doit retourner 401)
    print("\n🔑 Test avec token invalide...")
    try:
        headers = {'Authorization': 'Bearer invalid_token'}
        response = requests.get(f"{base_url}/admin/global_stats/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correct - Token invalide rejeté")
        else:
            print(f"   ❌ Inattendu: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")
    print("   - Si vous voyez des erreurs 500, le problème vient du code backend")
    print("   - Si vous voyez des erreurs 401, l'authentification fonctionne correctement")
    print("   - Le frontend doit se connecter avec le compte Super Admin 'window7'")

if __name__ == '__main__':
    test_auth()
