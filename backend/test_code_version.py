#!/usr/bin/env python
"""
Test pour vérifier quelle version du code est utilisée par le serveur
"""
import requests
import time

def test_code_version():
    """Tester quelle version du code est utilisée par le serveur"""
    print("🔍 Test pour vérifier quelle version du code est utilisée par le serveur...")
    
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
    
    # Test 2: Tentative de connexion
    print("\n🔑 Test 2: Tentative de connexion...")
    try:
        login_data = {
            "username": "window7",
            "password": "window7123"
        }
        
        login_response = requests.post(f"{base_url}/token/", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print(f"   ✅ Connexion réussie - Token obtenu")
            
            # Test 3: API avec authentification
            print("\n🚀 Test 3: API avec authentification...")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(f"{base_url}/admin/global_stats/", headers=headers)
            print(f"   📊 Status de l'API: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🎉 SUCCÈS ! Données reçues: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
                print(f"   💰 Total revenus: {data.get('total_revenue', 'N/A')}€")
            elif response.status_code == 500:
                print(f"   ❌ Erreur 500 - Code ancien encore actif")
                print(f"   📄 Erreur: {response.text[:500]}")
            else:
                print(f"   ❓ Status inattendu: {response.status_code}")
                
        else:
            print(f"   ❌ Échec de connexion: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")
    print("   - Si vous voyez 'SUCCÈS', le problème est complètement résolu !")
    print("   - Si vous voyez 'Code ancien encore actif', le serveur n'a pas été redémarré")

if __name__ == '__main__':
    test_code_version()
