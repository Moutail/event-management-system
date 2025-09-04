#!/usr/bin/env python3
"""
Script de test pour déboguer le problème de lancement automatique du stream
"""

import os
import sys
import django
import logging

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, VirtualEvent, EventRegistration
from django.utils import timezone
from datetime import timedelta

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

User = get_user_model()

def test_registration_flow():
    """Teste le flux d'inscription pour voir les logs"""
    print("🔍 TEST: Début du test d'inscription")
    
    try:
        # 1. Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_user_streaming',
            defaults={
                'email': 'test_streaming@example.com',
                'first_name': 'Test',
                'last_name': 'Streaming'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"✅ Utilisateur créé: {user.username}")
        else:
            print(f"✅ Utilisateur existant: {user.username}")
        
        # 2. Créer un événement virtuel de test
        event, created = Event.objects.get_or_create(
            title='Test Streaming Debug',
            defaults={
                'description': 'Événement de test pour déboguer le streaming',
                'start_date': timezone.now() + timedelta(hours=2),
                'end_date': timezone.now() + timedelta(hours=4),
                'location': 'En ligne',
                'event_type': 'virtual',
                'price': 0,
                'is_free': True,
                'status': 'published',
                'organizer': user
            }
        )
        if created:
            print(f"✅ Événement créé: {event.title}")
        else:
            print(f"✅ Événement existant: {event.title}")
        
        # 3. Créer les détails virtuels
        virtual_event, created = VirtualEvent.objects.get_or_create(
            event=event,
            defaults={
                'platform': 'zoom',
                'auto_record': False,
                'allow_chat': True,
                'allow_screen_sharing': True,
                'waiting_room': True
            }
        )
        if created:
            print(f"✅ Détails virtuels créés pour l'événement")
        else:
            print(f"✅ Détails virtuels existants pour l'événement")
        
        print(f"🔍 DEBUG: VirtualEvent ID: {virtual_event.id}")
        print(f"🔍 DEBUG: Meeting ID: {virtual_event.meeting_id}")
        print(f"🔍 DEBUG: Meeting URL: {virtual_event.meeting_url}")
        
        # 4. Créer une inscription (ce qui devrait déclencher les logs)
        print("\n🔍 TEST: Création de l'inscription...")
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={
                'status': 'confirmed',
                'payment_status': 'paid',
                'notes': 'Test de débogage streaming'
            }
        )
        if created:
            print(f"✅ Inscription créée: {registration.id}")
        else:
            print(f"✅ Inscription existante: {registration.id}")
            # Mettre à jour le statut pour déclencher les logs
            registration.status = 'confirmed'
            registration.payment_status = 'paid'
            registration.save()
            print(f"✅ Inscription mise à jour: {registration.id}")
        
        print(f"🔍 DEBUG: Registration ID: {registration.id}")
        print(f"🔍 DEBUG: Status: {registration.status}")
        print(f"🔍 DEBUG: Payment Status: {registration.payment_status}")
        
        # 5. Vérifier l'état final
        print("\n🔍 TEST: Vérification de l'état final...")
        registration.refresh_from_db()
        virtual_event.refresh_from_db()
        
        print(f"🔍 DEBUG: Final Registration Status: {registration.status}")
        print(f"🔍 DEBUG: Final Virtual Access Code: {registration.virtual_access_code}")
        print(f"🔍 DEBUG: Final Meeting ID: {virtual_event.meeting_id}")
        print(f"🔍 DEBUG: Final Meeting URL: {virtual_event.meeting_url}")
        
        print("\n✅ Test terminé - Vérifiez les logs du serveur pour voir ce qui s'est passé")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_registration_flow()
