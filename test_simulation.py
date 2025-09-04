#!/usr/bin/env python3
"""
Test du mode simulation
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent
from events.streaming_service import StreamingService

def test_simulation():
    """Test du mode simulation"""
    print("=== TEST MODE SIMULATION ===\n")
    
    try:
        # 1. Vérifier l'événement CONFER1
        print("1. Vérification de l'événement CONFER1...")
        event = Event.objects.get(title="CONFER1")
        print(f"   Event trouve: {event.title}")
        
        # 2. Vérifier le VirtualEvent
        print(f"\n2. Vérification du VirtualEvent...")
        virtual_event = event.virtual_details
        print(f"   VirtualEvent trouve: ID {virtual_event.id}")
        print(f"   Platform: {virtual_event.platform}")
        print(f"   Meeting ID AVANT: {virtual_event.meeting_id}")
        
        # 3. Tester la création de stream
        print(f"\n3. Test de la creation de stream...")
        
        streaming_service = StreamingService()
        
        try:
            result = streaming_service.create_stream_for_event(virtual_event)
            print(f"   Resultat: {result}")
            
            if result.get('success'):
                print(f"   SUCCES: Stream simule cree!")
                print(f"   Stream ID: {result.get('stream_id')}")
                print(f"   URL: {result.get('watch_url')}")
                
                # Vérifier en base
                virtual_event.refresh_from_db()
                print(f"   Meeting ID en base: {virtual_event.meeting_id}")
                print(f"   Meeting URL en base: {virtual_event.meeting_url}")
            else:
                print(f"   ERREUR: {result.get('error')}")
            
        except Exception as e:
            print(f"   EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n=== TEST TERMINE ===")
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simulation()
