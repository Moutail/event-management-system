#!/usr/bin/env python3
"""
Test direct de la route join_stream
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_route_direct():
    """Test direct de la route join_stream"""
    print("=== TEST DIRECT DE LA ROUTE JOIN_STREAM ===\n")
    
    try:
        # 1. Créer un client de test
        client = Client()
        
        # 2. Se connecter avec xchak475 (utilisateur non payé)
        print("1. Test avec xchak475 (utilisateur non payé)...")
        user = User.objects.get(username="xchak475")
        client.force_login(user)
        print(f"   ✅ Connecté en tant que: {user.username}")
        
        # 3. Appeler directement la route join_stream
        print(f"\n2. Appel direct de la route join_stream...")
        response = client.get('/api/streaming/92/join/')
        print(f"   Status Code: {response.status_code}")
        print(f"   Content: {response.content.decode()}")
        
        # 4. Analyser la réponse
        if response.status_code == 403:
            print(f"   ✅ SÉCURISATION OK: Accès refusé (403)")
            try:
                import json
                data = json.loads(response.content)
                print(f"   Erreur: {data.get('error')}")
                print(f"   Details: {data.get('details')}")
            except:
                print(f"   Réponse non-JSON")
        elif response.status_code == 200:
            print(f"   ❌ BRÈCHE DE SÉCURITÉ: Accès autorisé (200)")
        else:
            print(f"   ⚠️ Status inattendu: {response.status_code}")
        
        # 5. Test avec nealdov7 (utilisateur payé)
        print(f"\n3. Test avec nealdov7 (utilisateur payé)...")
        user_paid = User.objects.get(username="nealdov7")
        client.force_login(user_paid)
        print(f"   ✅ Connecté en tant que: {user_paid.username}")
        
        response_paid = client.get('/api/streaming/92/join/')
        print(f"   Status Code: {response_paid.status_code}")
        
        if response_paid.status_code == 200:
            print(f"   ✅ ACCÈS AUTORISÉ: Utilisateur payé")
        else:
            print(f"   ❌ PROBLÈME: Utilisateur payé bloqué ({response_paid.status_code})")
        
        print("\n=== TEST TERMINÉ ===")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_route_direct()
