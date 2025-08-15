#!/usr/bin/env python
"""
Test de l'API avec un vrai token JWT via HTTP
"""
import requests
import json

def test_real_jwt():
    """Tester l'API avec un vrai token JWT"""
    print("🔐 Test de l'API avec un vrai token JWT...")
    
    base_url = "http://localhost:8000/api"
    
    # 1. D'abord, se connecter pour obtenir un token
    print("\n🔑 Tentative de connexion...")
    try:
        login_data = {
            "username": "window7",
            "password": "test123"  # Remplacez par votre vrai mot de passe
        }
        
        login_response = requests.post(f"{base_url}/token/", json=login_data)
        print(f"   Status de connexion: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print(f"   ✅ Token obtenu: {access_token[:20]}...")
            
            # 2. Tester l'API avec le token
            print(f"\n🚀 Test de l'API avec le token...")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(f"{base_url}/admin/global_stats/", headers=headers)
            print(f"   Status de l'API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   🎉 SUCCÈS ! Données reçues: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
            else:
                print(f"   ❌ Erreur: {response.text[:200]}")
                
        else:
            print(f"   ❌ Échec de connexion: {login_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")
    print("   - Si vous voyez 'SUCCÈS', l'API fonctionne parfaitement !")
    print("   - Si vous voyez une erreur, le problème vient du frontend")

if __name__ == '__main__':
    test_real_jwt()
