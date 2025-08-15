#!/usr/bin/env python
"""
Test de connexion pour identifier le problème d'authentification
"""
import requests
import json

def test_login():
    """Tester la connexion et voir l'erreur exacte"""
    print("🔐 Test de connexion pour identifier le problème...")
    
    base_url = "http://localhost:8000/api"
    
    # Test de connexion
    print("\n🔑 Tentative de connexion...")
    try:
        login_data = {
            "username": "window7",
            "password": "window7123"
        }
        
        print(f"   📤 Envoi des données: {login_data}")
        login_response = requests.post(f"{base_url}/token/", json=login_data)
        print(f"   📥 Status de réponse: {login_response.status_code}")
        print(f"   📄 Contenu de la réponse: {login_response.text[:500]}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            print(f"   ✅ Connexion réussie - Token obtenu")
            
            # Test de l'API avec le token
            print(f"\n🚀 Test de l'API avec le token...")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(f"{base_url}/admin/global_stats/", headers=headers)
            print(f"   📊 Status de l'API: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   🎉 SUCCÈS ! Données reçues: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
                print(f"   💰 Total revenus: {data.get('total_revenue', 'N/A')}")
            else:
                print(f"   ❌ Erreur API: {response.text[:500]}")
                
        else:
            print(f"   ❌ Échec de connexion")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test de connexion terminé!")

if __name__ == '__main__':
    test_login()
