#!/usr/bin/env python
"""
🧪 TEST DE L'ENVOI MANUEL DES RAPPELS
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
from events.tasks import send_reminder_task

def test_manual_send():
    """Tester l'envoi manuel des rappels"""
    print("🧪 TEST DE L'ENVOI MANUEL DES RAPPELS")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_manual_send',
            defaults={
                'email': 'test@manual.com',
                'first_name': 'Test',
                'last_name': 'Manual'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Envoi Manuel',
            defaults={
                'description': 'Événement pour test envoi manuel',
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
                'guest_full_name': 'Test Guest Manual',
                'guest_email': 'guest@manual.com',
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
            title='Test Envoi Manuel Brouillon',
            message='Ce rappel est en brouillon et sera envoyé manuellement',
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
        
        # Envoi manuel
        print("🚀 Envoi manuel du rappel...")
        try:
            result = send_reminder_task(reminder1.id)
            print(f"✅ Résultat de l'envoi: {result}")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")
        
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
            title='Test Envoi Manuel Programmé',
            message='Ce rappel est programmé mais sera envoyé manuellement',
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
        
        # Envoi manuel
        print("🚀 Envoi manuel du rappel programmé...")
        try:
            result = send_reminder_task(reminder2.id)
            print(f"✅ Résultat de l'envoi: {result}")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")
        
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
    test_manual_send()

