#!/usr/bin/env python3
"""
Test du blocage des événements terminés
"""

import os
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent
from events.streaming_service import StreamingService
from django.contrib.auth.models import User
from django.utils import timezone

def test_event_blocking():
    """Test du blocage des événements terminés"""
    print("=== TEST DU BLOCAGE DES EVENEMENTS TERMINES ===\n")
    
    try:
        # 1. Vérifier l'événement CONFEMMA2
        print("1. Vérification de l'événement CONFEMMA2...")
        event = Event.objects.get(title="CONFEMMA2")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Date début: {event.start_date}")
        print(f"   Date fin: {event.end_date}")
        print(f"   Heure actuelle: {timezone.now()}")
        print(f"   Type: {event.event_type}")
        print(f"   Status: {event.status}")
        
        # 2. Tester les méthodes de validation
        print(f"\n2. Test des validations d'événement...")
        print(f"   Inscriptions ouvertes: {event.is_registration_open()}")
        print(f"   Streaming accessible: {event.is_streaming_accessible()}")
        print(f"   Statut inscriptions: {event.get_registration_status()}")
        print(f"   Message: {event.get_registration_message()}")
        
        # 3. Vérifier le VirtualEvent
        print(f"\n3. Vérification du VirtualEvent...")
        try:
            virtual_event = event.virtual_details
            print(f"   ✅ VirtualEvent trouvé: ID {virtual_event.id}")
            print(f"   Platform: {virtual_event.platform}")
            print(f"   Meeting ID: {virtual_event.meeting_id}")
        except VirtualEvent.DoesNotExist:
            print(f"   ❌ Aucun VirtualEvent configuré")
            return
        
        # 4. Tester le service de streaming (devrait échouer)
        print(f"\n4. Test du service de streaming...")
        streaming_service = StreamingService()
        result = streaming_service.start_stream(virtual_event)
        print(f"   Résultat: {result}")
        
        if result.get('success'):
            print("   ❌ ERREUR: Le stream a été lancé sur un événement terminé!")
        else:
            print(f"   ✅ CORRECT: Le stream est bloqué - {result.get('error')}")
        
        # 5. Créer un événement futur pour tester
        print(f"\n5. Test avec un événement futur...")
        future_event = Event.objects.create(
            title="Test Event Futur",
            description="Événement de test futur",
            start_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=2),
            event_type='virtual',
            organizer=User.objects.first(),
            status='published'
        )
        
        print(f"   ✅ Event futur créé: {future_event.title}")
        print(f"   Inscriptions ouvertes: {future_event.is_registration_open()}")
        print(f"   Streaming accessible: {future_event.is_streaming_accessible()}")
        print(f"   Statut: {future_event.get_registration_status()}")
        
        # Nettoyer
        future_event.delete()
        
        print("\n=== TESTS TERMINES ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_event_blocking()
