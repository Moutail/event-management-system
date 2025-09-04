#!/usr/bin/env python
"""
🧪 TEST RÉEL DE CRÉATION DE RAPPEL
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

def test_real_reminder_creation():
    """Tester la création réelle d'un rappel"""
    print("🧪 TEST RÉEL DE CRÉATION DE RAPPEL")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_real_creation',
            defaults={
                'email': 'test@realcreation.com',
                'first_name': 'Test',
                'last_name': 'RealCreation'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Création Réelle',
            defaults={
                'description': 'Événement pour tester la création réelle',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location',
                'max_capacity': 100,
                'price': 0,
                'organizer': user,
                'status': 'published'
            }
        )
        
        print(f"✅ Utilisateur: {user.username}")
        print(f"✅ Événement: {event.title}")
        print()
        
        # Test avec heure dans 2 minutes
        print("🧪 TEST: Création avec heure dans 2 minutes")
        print("-" * 50)
        
        future_time = timezone.now() + timedelta(minutes=2)
        print(f"Heure actuelle: {timezone.now()}")
        print(f"Heure programmée: {future_time}")
        print()
        
        # Créer le rappel
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Création Réelle',
            message='Ce rappel devrait être automatiquement en statut scheduled',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            scheduled_at=future_time,
            status='draft'  # Statut initial
        )
        
        print(f"Rappel créé:")
        print(f"  - ID: {reminder.id}")
        print(f"  - Titre: {reminder.title}")
        print(f"  - Statut initial: {reminder.status}")
        print(f"  - Heure programmée: {reminder.scheduled_at}")
        print()
        
        # Recharger depuis la base de données
        reminder.refresh_from_db()
        print(f"Après refresh_from_db():")
        print(f"  - Statut: {reminder.status}")
        print(f"  - Heure programmée: {reminder.scheduled_at}")
        print()
        
        # Vérifier si le rappel est dans la liste des rappels programmés
        scheduled_reminders = CustomReminder.objects.filter(status='scheduled')
        print(f"📊 Rappels programmés dans la base: {scheduled_reminders.count()}")
        
        if reminder in scheduled_reminders:
            print("✅ Le rappel est bien dans la liste des rappels programmés!")
        else:
            print("❌ Le rappel n'est PAS dans la liste des rappels programmés!")
        
        # Attendre 2 minutes et vérifier si le rappel est traité
        print("\n⏰ Attente de 2 minutes pour voir si le rappel est traité...")
        print("💡 Le système de rappels automatiques devrait traiter ce rappel")
        
        # Vérifier l'état actuel
        print(f"\n📊 État actuel:")
        print(f"  - Rappels programmés: {CustomReminder.objects.filter(status='scheduled').count()}")
        print(f"  - Rappels envoyés: {CustomReminder.objects.filter(status='sent').count()}")
        
        return reminder
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    reminder = test_real_reminder_creation()
    if reminder:
        print(f"\n🎯 Rappel créé avec ID: {reminder.id}")
        print("💡 Surveillez les logs du système de rappels automatiques")
        print("💡 Le rappel devrait être traité dans 2 minutes")

