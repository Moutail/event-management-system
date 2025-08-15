#!/usr/bin/env python
"""
Vérification après redémarrage du serveur
"""
import requests
import time

def verify_after_restart():
    """Vérifier que le serveur redémarré fonctionne"""
    print("🔍 Vérification après redémarrage du serveur...")
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(3)
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: API sans authentification (doit retourner 401)
    print("\n📊 Test 1: API sans authentification...")
    try:
        response = requests.get(f"{base_url}/admin/global_stats/")
        if response.status_code == 401:
            print("   ✅ Correct - Authentification requise")
        else:
            print(f"   ❌ Inattendu: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
    
    # Test 2: Tentative de connexion
    print("\n🔑 Test 2: Tentative de connexion...")
    try:
        login_data = {
            "username": "window7",
            "password": "test123"
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
            if response.status_code == 200:
                data = response.json()
                print(f"   🎉 SUCCÈS ! Données reçues: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
                print(f"   💰 Total revenus: {data.get('total_revenue', 'N/A')}€")
            else:
                print(f"   ❌ Erreur: {response.status_code} - {response.text[:200]}")
                
        else:
            print(f"   ❌ Échec de connexion: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Vérification terminée!")
    print("   - Si vous voyez 'SUCCÈS', le problème est résolu !")
    print("   - Si vous voyez encore des erreurs, le serveur n'a pas été redémarré")

if __name__ == '__main__':
    verify_after_restart()
