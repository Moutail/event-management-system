#!/usr/bin/env python
"""
🧪 TEST DE L'ENVOI MANUEL VIA send_now
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.utils import timezone
from events.models import CustomReminder, Event, EventRegistration, User
from events.views import CustomReminderViewSet
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser

def test_send_now():
    """Tester l'envoi manuel via send_now"""
    print("🧪 TEST DE L'ENVOI MANUEL VIA send_now")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_send_now',
            defaults={
                'email': 'test@sendnow.com',
                'first_name': 'Test',
                'last_name': 'SendNow'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Send Now',
            defaults={
                'description': 'Événement pour test send_now',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location',
                'max_capacity': 100,
                'price': 0,
                'organizer': user,
                'status': 'published'
            }
        )
        
        # Créer des inscriptions de test
        registration1, created = EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={
                'status': 'confirmed',
                'price_paid': 0,
                'payment_status': 'paid'
            }
        )
        
        # Créer une inscription invité
        registration2, created = EventRegistration.objects.get_or_create(
            event=event,
            user=None,
            defaults={
                'status': 'confirmed',
                'price_paid': 0,
                'payment_status': 'paid',
                'guest_full_name': 'Test Guest SendNow',
                'guest_email': 'guest@sendnow.com',
                'guest_phone': '5141234567'
            }
        )
        
        print(f"✅ Utilisateur: {user.username}")
        print(f"✅ Événement: {event.title}")
        print(f"✅ Inscriptions: {event.registrations.count()}")
        print()
        
        # Test 1: Envoi manuel d'un rappel en brouillon
        print("🧪 TEST 1: Envoi manuel d'un rappel en brouillon")
        print("-" * 50)
        
        reminder1 = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Send Now Brouillon',
            message='Ce rappel est en brouillon et sera envoyé manuellement via send_now',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            status='draft'  # Statut brouillon
        )
        
        print(f"Rappel créé:")
        print(f"  - ID: {reminder1.id}")
        print(f"  - Titre: {reminder1.title}")
        print(f"  - Statut: {reminder1.status}")
        print(f"  - Destinataires: {reminder1.get_recipients().count()}")
        print()
        
        # Simuler l'appel à send_now
        print("🚀 Envoi manuel via send_now...")
        
        # Créer une requête simulée
        factory = APIRequestFactory()
        request = factory.post(f'/custom-reminders/{reminder1.id}/send_now/')
        request.user = user
        
        # Créer l'instance de la vue
        viewset = CustomReminderViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        
        # Appeler send_now
        try:
            response = viewset.send_now(request, pk=reminder1.id)
            print(f"✅ Réponse de send_now: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"✅ Données de réponse: {response.data}")
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à send_now: {e}")
            import traceback
            traceback.print_exc()
        
        # Vérifier le statut après envoi
        reminder1.refresh_from_db()
        print(f"Statut après envoi: {reminder1.status}")
        print()
        
        # Test 2: Envoi manuel d'un rappel programmé
        print("🧪 TEST 2: Envoi manuel d'un rappel programmé")
        print("-" * 50)
        
        future_time = timezone.now() + timedelta(minutes=5)
        reminder2 = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Send Now Programmé',
            message='Ce rappel est programmé mais sera envoyé manuellement via send_now',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            scheduled_at=future_time,
            status='scheduled'  # Statut programmé
        )
        
        print(f"Rappel créé:")
        print(f"  - ID: {reminder2.id}")
        print(f"  - Titre: {reminder2.title}")
        print(f"  - Statut: {reminder2.status}")
        print(f"  - Heure programmée: {reminder2.scheduled_at}")
        print(f"  - Destinataires: {reminder2.get_recipients().count()}")
        print()
        
        # Simuler l'appel à send_now
        print("🚀 Envoi manuel via send_now...")
        
        # Créer une requête simulée
        request2 = factory.post(f'/custom-reminders/{reminder2.id}/send_now/')
        request2.user = user
        
        # Appeler send_now
        try:
            response2 = viewset.send_now(request2, pk=reminder2.id)
            print(f"✅ Réponse de send_now: {response2.status_code}")
            if hasattr(response2, 'data'):
                print(f"✅ Données de réponse: {response2.data}")
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à send_now: {e}")
            import traceback
            traceback.print_exc()
        
        # Vérifier le statut après envoi
        reminder2.refresh_from_db()
        print(f"Statut après envoi: {reminder2.status}")
        print()
        
        # Résumé des tests
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        print(f"Test 1 (brouillon): {reminder1.status} ✅" if reminder1.status == 'sent' else f"Test 1 (brouillon): {reminder1.status} ❌")
        print(f"Test 2 (programmé): {reminder2.status} ✅" if reminder2.status == 'sent' else f"Test 2 (programmé): {reminder2.status} ❌")
        
        # Nettoyage
        print("\n🧹 Nettoyage des tests...")
        reminder1.delete()
        reminder2.delete()
        print("✅ Tests nettoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_send_now()

