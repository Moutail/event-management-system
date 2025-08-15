#!/usr/bin/env python
"""
Test pour vérifier quelle version du code est utilisée
"""
import requests
import time

def test_version():
    """Tester quelle version du code est utilisée"""
    print("🔍 Test pour vérifier quelle version du code est utilisée...")
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: API sans authentification (doit retourner 401)
    print("\n📊 Test 1: API sans authentification...")
    try:
        response = requests.get(f"{base_url}/admin/global_stats/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 500:
            print(f"   ❌ Erreur 500 - Code ancien encore actif")
            print(f"   📄 Erreur: {response.text[:500]}")
        elif response.status_code == 401:
            print(f"   ✅ Status 401 - Code corrigé actif")
        else:
            print(f"   ❓ Status inattendu: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
    
    print("\n🎯 Test terminé!")
    print("   - Si vous voyez 'Code corrigé actif', le problème est résolu !")
    print("   - Si vous voyez 'Code ancien encore actif', le serveur n'a pas été redémarré")

if __name__ == '__main__':
    test_version()
