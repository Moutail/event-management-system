#!/usr/bin/env python
"""
🧪 TEST COMPLET AVEC DESTINATAIRES
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

def test_complete_reminder():
    """Test complet avec destinataires"""
    print("🧪 TEST COMPLET AVEC DESTINATAIRES")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_complete',
            defaults={
                'email': 'test@complete.com',
                'first_name': 'Test',
                'last_name': 'Complete'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Complet',
            defaults={
                'description': 'Événement pour test complet',
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
                'guest_full_name': 'Test Guest',
                'guest_email': 'guest@test.com',
                'guest_phone': '5141234567'
            }
        )
        
        print(f"✅ Utilisateur: {user.username}")
        print(f"✅ Événement: {event.title}")
        print(f"✅ Inscriptions: {event.registrations.count()}")
        print()
        
        # Créer un rappel avec heure dans 1 minute
        future_time = timezone.now() + timedelta(minutes=1)
        print(f"Heure actuelle: {timezone.now()}")
        print(f"Heure programmée: {future_time}")
        print()
        
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Complet Final',
            message='Ce rappel devrait être envoyé automatiquement avec des destinataires',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,  # Désactiver SMS pour éviter la limite Twilio
            scheduled_at=future_time,
            status='draft'
        )
        
        print(f"Rappel créé:")
        print(f"  - ID: {reminder.id}")
        print(f"  - Titre: {reminder.title}")
        print(f"  - Statut: {reminder.status}")
        print(f"  - Heure programmée: {reminder.scheduled_at}")
        print(f"  - Destinataires: {reminder.get_recipients().count()}")
        print()
        
        # Vérifier les destinataires
        recipients = reminder.get_recipients()
        print(f"📋 Destinataires trouvés:")
        for recipient in recipients:
            if recipient.user:
                print(f"  - Utilisateur: {recipient.user.username} ({recipient.user.email})")
            else:
                print(f"  - Invité: {recipient.guest_full_name} ({recipient.guest_email})")
        print()
        
        print("⏰ Le rappel sera traité dans 1 minute par le système automatique")
        print("💡 Surveillez les logs pour voir l'envoi automatique")
        
        return reminder
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    reminder = test_complete_reminder()
    if reminder:
        print(f"\n🎯 Rappel créé avec ID: {reminder.id}")
        print("💡 Le rappel sera envoyé automatiquement dans 1 minute")

