#!/usr/bin/env python3
"""
Test final de la correction - Vérification que les organisateurs peuvent accéder au streaming
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

import requests
import json

def test_final_correction():
    """Test final de la correction"""
    print("=== TEST FINAL DE LA CORRECTION ===\n")
    
    # URL de base
    base_url = "http://127.0.0.1:8001"
    
    try:
        # 1. Se connecter avec nealdov7 (organisateur de l'événement 93)
        print("1. Connexion avec nealdov7 (organisateur de l'événement 93)...")
        
        login_data = {
            "username": "nealdov7",
            "password": "test123"
        }
        
        response = requests.post(f"{base_url}/api/auth/token/", data=login_data)
        if response.status_code == 200:
            token = response.json()["access"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ Connecté en tant que: {login_data['username']}")
        else:
            print(f"   ❌ Échec de connexion: {response.status_code}")
            return
        
        # 2. Test de l'API start_stream avec nealdov7 (organisateur)
        print(f"\n2. Test de l'API start_stream avec nealdov7 (organisateur)...")
        response_start = requests.post(f"{base_url}/api/streaming/93/start/", headers=headers)
        print(f"   Status Code: {response_start.status_code}")
        
        if response_start.status_code == 200:
            print(f"   ✅ ORGANISATEUR AUTORISÉ: Peut lancer le stream")
            try:
                data = response_start.json()
                print(f"   Message: {data.get('message')}")
            except:
                print(f"   Réponse non-JSON")
        else:
            print(f"   ❌ PROBLÈME: Organisateur bloqué ({response_start.status_code})")
            try:
                data = response_start.json()
                print(f"   Erreur: {data.get('error')}")
            except:
                print(f"   Réponse non-JSON")
        
        # 3. Test de l'API join_stream avec nealdov7 (organisateur)
        print(f"\n3. Test de l'API join_stream avec nealdov7 (organisateur)...")
        response_join = requests.post(f"{base_url}/api/streaming/93/join/", headers=headers)
        print(f"   Status Code: {response_join.status_code}")
        
        if response_join.status_code == 200:
            print(f"   ✅ ORGANISATEUR AUTORISÉ: Peut rejoindre le stream")
            try:
                data = response_join.json()
                print(f"   Meeting URL: {data.get('stream_info', {}).get('meeting_url')}")
            except:
                print(f"   Réponse non-JSON")
        else:
            print(f"   ❌ PROBLÈME: Organisateur bloqué ({response_join.status_code})")
            try:
                data = response_join.json()
                print(f"   Erreur: {data.get('error')}")
            except:
                print(f"   Réponse non-JSON")
        
        # 4. Se connecter avec xchak475 (utilisateur non payé)
        print(f"\n4. Connexion avec xchak475 (utilisateur non payé)...")
        
        login_data_other = {
            "username": "xchak475",
            "password": "test123"
        }
        
        response_other = requests.post(f"{base_url}/api/auth/token/", data=login_data_other)
        if response_other.status_code == 200:
            token_other = response_other.json()["access"]
            headers_other = {"Authorization": f"Bearer {token_other}"}
            print(f"   ✅ Connecté en tant que: {login_data_other['username']}")
        else:
            print(f"   ❌ Échec de connexion: {response_other.status_code}")
            return
        
        # 5. Test de l'API join_stream avec xchak475 (utilisateur non payé)
        print(f"\n5. Test de l'API join_stream avec xchak475 (utilisateur non payé)...")
        response_other_join = requests.post(f"{base_url}/api/streaming/93/join/", headers=headers_other)
        print(f"   Status Code: {response_other_join.status_code}")
        
        if response_other_join.status_code == 403:
            print(f"   ✅ SÉCURISATION OK: Utilisateur non payé bloqué (403)")
            try:
                data = response_other_join.json()
                print(f"   Erreur: {data.get('error')}")
                print(f"   Details: {data.get('details')}")
            except:
                print(f"   Réponse non-JSON")
        else:
            print(f"   ❌ PROBLÈME: Utilisateur non payé autorisé ({response_other_join.status_code})")
            try:
                data = response_other_join.json()
                print(f"   Réponse: {data}")
            except:
                print(f"   Réponse non-JSON")
        
        print("\n=== RÉSULTAT FINAL ===")
        print("✅ MIDDLEWARE: Désactivé (problème d'authentification JWT)")
        print("✅ SÉCURISATION: Directement dans les vues")
        print("✅ ORGANISATEURS: Doivent être autorisés")
        print("✅ UTILISATEURS NON PAYÉS: Doivent être bloqués")
        
        if response_start.status_code == 200 and response_join.status_code == 200 and response_other_join.status_code == 403:
            print("\n🎉 CORRECTION RÉUSSIE !")
            print("✅ Les organisateurs peuvent lancer et rejoindre le stream")
            print("✅ Les utilisateurs non payés sont bloqués")
        else:
            print("\n❌ PROBLÈME PERSISTANT !")
            print("   Vérifiez les logs du serveur Django")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_correction()
