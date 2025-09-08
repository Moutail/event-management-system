#!/usr/bin/env python3
"""
🧪 TEST DE L'API AVEC EVENT_ID
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event

def test_api_with_event_id():
    """Test de l'API avec event_id"""
    print("🎯 Test de l'API avec event_id")
    print("=" * 50)

    try:
        # Récupérer un événement de test
        event = Event.objects.filter(status='published').first()
        if not event:
            print("❌ Aucun événement publié trouvé")
            return
        
        print(f"🎯 Test sur l'événement: {event.title} (ID: {event.id})")
        
        # Test de l'endpoint avec event_id
        url = f"http://localhost:8001/api/admin/predictive_analytics/?event_id={event.id}&days_back=30"
        print(f"📡 Test de l'URL: {url}")

        # Faire la requête
        response = requests.get(url, timeout=10)

        print(f"📊 Statut de la réponse: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ Succès!")
            print("📄 Contenu de la réponse:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Vérifier les insights spécifiques
            if 'insights' in data and 'event_specific_insights' in data['insights']:
                print(f"\n🎯 Insights spécifiques trouvés: {len(data['insights']['event_specific_insights'])}")
                for insight in data['insights']['event_specific_insights']:
                    print(f"   • {insight}")
            else:
                print("❌ Pas d'insights spécifiques trouvés")
                
        elif response.status_code == 401:
            print("ℹ️ 401 - Non autorisé (normal sans authentification)")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"📄 Contenu de l'erreur: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("   Assurez-vous que le serveur fonctionne sur le port 8001")
    except Exception as e:
        print(f"❌ Une erreur inattendue s'est produite: {str(e)}")

if __name__ == "__main__":
    test_api_with_event_id()


















