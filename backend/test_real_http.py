#!/usr/bin/env python3
"""
Test avec de vraies requêtes HTTP pour tester le middleware
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

import requests
import json

def test_real_http():
    """Test avec de vraies requêtes HTTP"""
    print("=== TEST AVEC DE VRAIES REQUÊTES HTTP ===\n")
    
    # URL de base
    base_url = "http://127.0.0.1:8001"
    
    try:
        # 1. Se connecter avec xchak475 (utilisateur non payé)
        print("1. Connexion avec xchak475 (utilisateur non payé)...")
        
        login_data = {
            "username": "xchak475",
            "password": "test123"
        }
        
        response = requests.post(f"{base_url}/api/auth/token/", data=login_data)
        if response.status_code == 200:
            token = response.json()["access"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ Connecté en tant que: xchak475")
        else:
            print(f"   ❌ Échec de connexion: {response.status_code}")
            return
        
        # 2. Test de l'API join_stream avec xchak475
        print(f"\n2. Test de l'API join_stream avec xchak475...")
        response = requests.post(f"{base_url}/api/streaming/93/join/", headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print(f"   ✅ SÉCURISATION OK: Utilisateur non payé bloqué (403)")
            try:
                data = response.json()
                print(f"   Erreur: {data.get('error')}")
                print(f"   Details: {data.get('details')}")
            except:
                print(f"   Réponse non-JSON")
        else:
            print(f"   ❌ PROBLÈME: Utilisateur non payé autorisé ({response.status_code})")
            try:
                data = response.json()
                print(f"   Réponse: {data}")
            except:
                print(f"   Réponse non-JSON")
        
        # 3. Se connecter avec nealdov7 (organisateur)
        print(f"\n3. Connexion avec nealdov7 (organisateur)...")
        
        login_data_org = {
            "username": "nealdov7",
            "password": "test123"
        }
        
        response_org = requests.post(f"{base_url}/api/auth/token/", data=login_data_org)
        if response_org.status_code == 200:
            token_org = response_org.json()["access"]
            headers_org = {"Authorization": f"Bearer {token_org}"}
            print(f"   ✅ Connecté en tant que: nealdov7")
        else:
            print(f"   ❌ Échec de connexion: {response_org.status_code}")
            return
        
        # 4. Test de l'API join_stream avec nealdov7
        print(f"\n4. Test de l'API join_stream avec nealdov7...")
        response_org_join = requests.post(f"{base_url}/api/streaming/93/join/", headers=headers_org)
        print(f"   Status Code: {response_org_join.status_code}")
        
        if response_org_join.status_code == 200:
            print(f"   ✅ ORGANISATEUR AUTORISÉ: Peut rejoindre le stream")
            try:
                data = response_org_join.json()
                print(f"   Meeting URL: {data.get('stream_info', {}).get('meeting_url')}")
            except:
                print(f"   Réponse non-JSON")
        else:
            print(f"   ❌ PROBLÈME: Organisateur bloqué ({response_org_join.status_code})")
        
        print("\n=== RÉSULTAT FINAL ===")
        print("✅ MIDDLEWARE: Testé avec de vraies requêtes HTTP")
        print("✅ SÉCURISATION: Doit bloquer les utilisateurs non payés")
        print("✅ ORGANISATEURS: Doivent être autorisés")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_http()
