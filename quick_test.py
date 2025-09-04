#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event
from events.streaming_service import StreamingService

def test():
    print("=== TEST RAPIDE ===")
    try:
        event = Event.objects.get(title="CONFER1")
        virtual_event = event.virtual_details
        print(f"Event: {event.title}")
        print(f"Platform: {virtual_event.platform}")
        print(f"Meeting ID avant: {virtual_event.meeting_id}")
        
        service = StreamingService()
        result = service.create_stream_for_event(virtual_event)
        print(f"Resultat: {result}")
        
        if result.get('success'):
            virtual_event.refresh_from_db()
            print(f"Meeting ID apres: {virtual_event.meeting_id}")
            print(f"Meeting URL apres: {virtual_event.meeting_url}")
            print("SUCCES!")
        else:
            print(f"ERREUR: {result.get('error')}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
