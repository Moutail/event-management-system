#!/usr/bin/env python
"""
🧪 TEST DU STATUT AUTOMATIQUE DES RAPPELS
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

def test_automatic_status():
    """Tester le changement automatique de statut"""
    print("🧪 TEST DU STATUT AUTOMATIQUE DES RAPPELS")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_auto_status',
            defaults={
                'email': 'test@autostatus.com',
                'first_name': 'Test',
                'last_name': 'AutoStatus'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Statut Automatique',
            defaults={
                'description': 'Événement pour tester le statut automatique',
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
        
        # Test 1: Créer un rappel avec heure dans le futur
        print("🧪 TEST 1: Rappel avec heure dans le futur")
        print("-" * 40)
        
        future_time = timezone.now() + timedelta(minutes=5)
        reminder1 = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Statut Futur',
            message='Ce rappel devrait être automatiquement en statut scheduled',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            scheduled_at=future_time,
            status='draft'  # Statut initial
        )
        
        print(f"Rappel créé avec statut: {reminder1.status}")
        print(f"Heure programmée: {reminder1.scheduled_at}")
        
        # Recharger depuis la base de données
        reminder1.refresh_from_db()
        print(f"Statut après save(): {reminder1.status}")
        print()
        
        # Test 2: Créer un rappel avec heure dans le passé
        print("🧪 TEST 2: Rappel avec heure dans le passé")
        print("-" * 40)
        
        past_time = timezone.now() - timedelta(minutes=5)
        reminder2 = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Statut Passé',
            message='Ce rappel devrait rester en statut draft',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            scheduled_at=past_time,
            status='draft'  # Statut initial
        )
        
        print(f"Rappel créé avec statut: {reminder2.status}")
        print(f"Heure programmée: {reminder2.scheduled_at}")
        
        # Recharger depuis la base de données
        reminder2.refresh_from_db()
        print(f"Statut après save(): {reminder2.status}")
        print()
        
        # Test 3: Modifier un rappel existant
        print("🧪 TEST 3: Modification d'un rappel existant")
        print("-" * 40)
        
        reminder3 = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Modification',
            message='Ce rappel sera modifié',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            status='draft'
        )
        
        print(f"Rappel créé avec statut: {reminder3.status}")
        
        # Modifier l'heure programmée
        future_time2 = timezone.now() + timedelta(minutes=10)
        reminder3.scheduled_at = future_time2
        reminder3.save()
        
        print(f"Heure programmée: {reminder3.scheduled_at}")
        print(f"Statut après modification: {reminder3.status}")
        print()
        
        # Résumé des tests
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        print(f"Test 1 (futur): {reminder1.status} ✅" if reminder1.status == 'scheduled' else f"Test 1 (futur): {reminder1.status} ❌")
        print(f"Test 2 (passé): {reminder2.status} ✅" if reminder2.status == 'draft' else f"Test 2 (passé): {reminder2.status} ❌")
        print(f"Test 3 (modification): {reminder3.status} ✅" if reminder3.status == 'scheduled' else f"Test 3 (modification): {reminder3.status} ❌")
        
        # Nettoyage
        print("\n🧹 Nettoyage des tests...")
        reminder1.delete()
        reminder2.delete()
        reminder3.delete()
        print("✅ Tests nettoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_automatic_status()
