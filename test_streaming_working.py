#!/usr/bin/env python3
"""
Test du streaming qui fonctionne maintenant
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent
from events.streaming_service import StreamingService

def test_streaming_working():
    """Test du streaming qui fonctionne"""
    print("=== TEST STREAMING QUI FONCTIONNE ===\n")
    
    try:
        # 1. Vérifier l'événement CONFER1
        print("1. Vérification de l'événement CONFER1...")
        event = Event.objects.get(title="CONFER1")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Type: {event.event_type}")
        print(f"   Organisateur: {event.organizer.username}")
        
        # 2. Vérifier le VirtualEvent
        print(f"\n2. Vérification du VirtualEvent...")
        try:
            virtual_event = event.virtual_details
            print(f"   ✅ VirtualEvent trouvé: ID {virtual_event.id}")
            print(f"   Platform: {virtual_event.platform}")
            print(f"   Meeting ID AVANT: {virtual_event.meeting_id}")
            print(f"   Meeting URL AVANT: {virtual_event.meeting_url}")
        except VirtualEvent.DoesNotExist:
            print(f"   ❌ Aucun VirtualEvent configuré")
            return
        
        # 3. Tester le démarrage du stream
        print(f"\n3. Test du démarrage du stream...")
        
        streaming_service = StreamingService()
        
        try:
            result = streaming_service.start_stream(virtual_event)
            print(f"   ✅ Stream démarré avec succès: {result}")
            
            # Vérifier que les identifiants sont maintenant présents
            virtual_event.refresh_from_db()
            print(f"   Meeting ID APRÈS: {virtual_event.meeting_id}")
            print(f"   Meeting URL APRÈS: {virtual_event.meeting_url}")
            
            if result.get('success'):
                print(f"   🎉 STREAMING FONCTIONNE !")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"   ❌ Erreur: {result.get('error')}")
            
        except Exception as e:
            print(f"   ❌ Erreur démarrage stream: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n=== TEST TERMINE ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streaming_working()
