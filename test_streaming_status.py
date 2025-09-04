#!/usr/bin/env python3
"""
Test de l'API de streaming status
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent
from events.streaming_views import get_stream_status
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate

def test_streaming_status():
    """Test de l'API de streaming status"""
    print("=== TEST API STREAMING STATUS ===\n")
    
    try:
        # 1. Vérifier l'événement CONFEMMA2
        print("1. Vérification de l'événement CONFEMMA2...")
        event = Event.objects.get(title="CONFEMMA2")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Type: {event.event_type}")
        print(f"   Date fin: {event.end_date}")
        print(f"   Streaming accessible: {event.is_streaming_accessible()}")
        
        # 2. Vérifier le VirtualEvent
        print(f"\n2. Vérification du VirtualEvent...")
        try:
            virtual_event = event.virtual_details
            print(f"   ✅ VirtualEvent trouvé: ID {virtual_event.id}")
            print(f"   Platform: {virtual_event.platform}")
            print(f"   Meeting ID: {virtual_event.meeting_id}")
        except VirtualEvent.DoesNotExist:
            print(f"   ❌ Aucun VirtualEvent configuré")
            return
        
        # 3. Tester l'API de streaming status
        print(f"\n3. Test de l'API de streaming status...")
        
        # Créer une requête de test
        factory = APIRequestFactory()
        request = factory.get(f'/api/streaming/{event.id}/status/')
        
        # Authentifier avec un utilisateur
        user = User.objects.first()
        if user:
            force_authenticate(request, user=user)
            print(f"   Utilisateur authentifié: {user.username}")
            
            # Appeler la vue
            from rest_framework.response import Response
            response = get_stream_status(request, event.id)
            
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.data}")
            
            if response.status_code == 200:
                print(f"   ✅ API fonctionne correctement")
                if response.data.get('streaming_available'):
                    print(f"   ✅ Streaming disponible")
                else:
                    print(f"   ℹ️ Streaming non disponible (événement terminé)")
            else:
                print(f"   ❌ Erreur API: {response.status_code}")
        else:
            print(f"   ⚠️ Aucun utilisateur trouvé pour le test")
        
        print("\n=== TEST TERMINE ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streaming_status()
