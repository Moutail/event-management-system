#!/usr/bin/env python3
"""
Test du système de streaming corrigé
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import VirtualEvent
from events.streaming_service import StreamingService

def test_streaming_corrected():
    """Test du système de streaming corrigé"""
    print("=== TEST DU SYSTEME DE STREAMING CORRIGE ===\n")
    
    try:
        # 1. Vérifier qu'il y a des événements virtuels
        virtual_events = VirtualEvent.objects.all()
        if not virtual_events.exists():
            print("❌ Aucun événement virtuel trouvé")
            return
        
        virtual_event = virtual_events.first()
        print(f"✅ VirtualEvent trouvé: ID {virtual_event.id}")
        print(f"   Event: {virtual_event.event.title}")
        print(f"   Platform: {virtual_event.platform}")
        print(f"   Meeting ID: {virtual_event.meeting_id}")
        
        # 2. Tester le service de streaming
        print(f"\n2. Test du StreamingService...")
        streaming_service = StreamingService()
        print(f"   ✅ StreamingService créé")
        
        # 3. Tester start_stream
        print(f"\n3. Test de start_stream...")
        result = streaming_service.start_stream(virtual_event)
        print(f"   Résultat: {result}")
        
        if result.get('success'):
            print("   ✅ Stream démarré avec succès")
        else:
            print(f"   ⚠️ Erreur: {result.get('error')}")
            print(f"   Status: {result.get('status', 'N/A')}")
        
        # 4. Tester stop_stream
        print(f"\n4. Test de stop_stream...")
        result_stop = streaming_service.stop_stream(virtual_event)
        print(f"   Résultat: {result_stop}")
        
        if result_stop.get('success'):
            print("   ✅ Stream arrêté avec succès")
        else:
            print(f"   ⚠️ Erreur: {result_stop.get('error')}")
        
        print("\n=== TEST TERMINÉ ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_streaming_corrected()
