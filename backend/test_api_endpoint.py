#!/usr/bin/env python3
"""
🧪 TEST DE L'ENDPOINT API PREDICTIVE ANALYTICS
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def test_api_endpoint():
    """Test de l'endpoint de l'API"""
    print("🎯 Test de l'endpoint API Predictive Analytics")
    print("=" * 50)
    
    try:
        # Test de l'endpoint
        url = "http://localhost:8001/api/admin/predictive_analytics/?days_back=30"
        
        print(f"📡 Test de l'URL: {url}")
        
        # Faire la requête
        response = requests.get(url, timeout=10)
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Succès ! L'API fonctionne correctement")
            try:
                data = response.json()
                print(f"📄 Données reçues: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("⚠️ Réponse reçue mais pas de JSON valide")
                print(f"📄 Contenu brut: {response.text[:500]}")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"📄 Contenu de l'erreur: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("   Assurez-vous que le serveur fonctionne sur le port 8001")
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoint()















