#!/usr/bin/env python3
"""
Test des corrections du système de streaming
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent, EventRegistration
from events.streaming_service import StreamingService

def test_streaming_fixed():
    """Test des corrections du streaming"""
    print("=== TEST DES CORRECTIONS STREAMING ===\n")
    
    try:
        # 1. Vérifier l'événement CONFERENCE2025
        print("1. Vérification de l'événement CONFERENCE2025...")
        event = Event.objects.get(title="CONFERENCE2025")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Type: {event.event_type}")
        print(f"   Organisateur: {event.organizer.username}")
        
        # 2. Vérifier le VirtualEvent
        print(f"\n2. Vérification du VirtualEvent...")
        try:
            virtual_event = event.virtual_details
            print(f"   ✅ VirtualEvent trouvé: ID {virtual_event.id}")
            print(f"   Platform: {virtual_event.platform}")
            print(f"   Meeting ID: {virtual_event.meeting_id}")
            print(f"   Meeting URL: {virtual_event.meeting_url}")
        except VirtualEvent.DoesNotExist:
            print(f"   ❌ Aucun VirtualEvent configuré")
            return
        
        # 3. Tester la création de stream
        print(f"\n3. Test de la création de stream...")
        
        streaming_service = StreamingService()
        
        try:
            result = streaming_service.create_stream_for_event(virtual_event)
            print(f"   ✅ Stream créé avec succès: {result}")
            
            # Vérifier que les identifiants sont maintenant présents
            virtual_event.refresh_from_db()
            print(f"   Meeting ID après création: {virtual_event.meeting_id}")
            print(f"   Meeting URL après création: {virtual_event.meeting_url}")
            
        except Exception as e:
            print(f"   ❌ Erreur création stream: {e}")
        
        # 4. Vérifier les inscriptions
        print(f"\n4. Vérification des inscriptions...")
        registrations = EventRegistration.objects.filter(event=event)
        print(f"   Total inscriptions: {registrations.count()}")
        
        for reg in registrations:
            print(f"   - {reg.user.username}: {reg.status}")
            print(f"     Email: {reg.user.email}")
        
        print("\n=== TEST TERMINE ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streaming_fixed()
