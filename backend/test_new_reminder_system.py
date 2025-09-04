#!/usr/bin/env python
"""
🧪 TEST DU NOUVEAU SYSTÈME DE RAPPELS
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
from events.serializers import CustomReminderSerializer
from rest_framework.test import APIRequestFactory

def test_new_reminder_system():
    """Tester le nouveau système de rappels"""
    print("🧪 TEST DU NOUVEAU SYSTÈME DE RAPPELS")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_new_system',
            defaults={
                'email': 'test@newsystem.com',
                'first_name': 'Test',
                'last_name': 'NewSystem'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Nouveau Système',
            defaults={
                'description': 'Événement pour test nouveau système',
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
        
        print(f"✅ Utilisateur: {user.username}")
        print(f"✅ Événement: {event.title}")
        print(f"✅ Inscriptions: {event.registrations.count()}")
        print()
        
        # Test 1: Création d'un rappel en mode manuel
        print("🧪 TEST 1: Création d'un rappel en mode manuel")
        print("-" * 50)
        
        factory = APIRequestFactory()
        request = factory.post('/api/custom-reminders/')
        request.user = user
        
        reminder_data_manual = {
            'event': event.id,
            'title': 'Test Mode Manuel',
            'message': 'Ce rappel est créé en mode manuel',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'send_mode': 'manual'  # Mode manuel
        }
        
        serializer = CustomReminderSerializer(data=reminder_data_manual, context={'request': request})
        if serializer.is_valid():
            reminder_manual = serializer.save()
            print(f"✅ Rappel manuel créé:")
            print(f"   - ID: {reminder_manual.id}")
            print(f"   - Titre: {reminder_manual.title}")
            print(f"   - Statut: {reminder_manual.status}")
            print(f"   - Mode: Manuel")
        else:
            print(f"❌ Erreur validation manuel: {serializer.errors}")
        
        print()
        
        # Test 2: Création d'un rappel en mode automatique
        print("🧪 TEST 2: Création d'un rappel en mode automatique")
        print("-" * 50)
        
        future_time = timezone.now() + timedelta(minutes=2)
        reminder_data_auto = {
            'event': event.id,
            'title': 'Test Mode Automatique',
            'message': 'Ce rappel est créé en mode automatique',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'scheduled_at': future_time,
            'send_mode': 'automatic'  # Mode automatique
        }
        
        serializer = CustomReminderSerializer(data=reminder_data_auto, context={'request': request})
        if serializer.is_valid():
            reminder_auto = serializer.save()
            print(f"✅ Rappel automatique créé:")
            print(f"   - ID: {reminder_auto.id}")
            print(f"   - Titre: {reminder_auto.title}")
            print(f"   - Statut: {reminder_auto.status}")
            print(f"   - Heure programmée: {reminder_auto.scheduled_at}")
            print(f"   - Mode: Automatique")
        else:
            print(f"❌ Erreur validation automatique: {serializer.errors}")
        
        print()
        
        # Test 3: Test de l'envoi manuel du rappel en brouillon
        print("🧪 TEST 3: Envoi manuel du rappel en brouillon")
        print("-" * 50)
        
        if 'reminder_manual' in locals():
            from events.tasks import send_reminder_task
            print(f"🚀 Envoi manuel du rappel {reminder_manual.id}...")
            try:
                result = send_reminder_task(reminder_manual.id)
                print(f"✅ Résultat envoi manuel: {result}")
                
                # Vérifier le statut après envoi
                reminder_manual.refresh_from_db()
                print(f"📊 Statut après envoi: {reminder_manual.status}")
            except Exception as e:
                print(f"❌ Erreur envoi manuel: {e}")
        
        print()
        
        # Test 4: Traitement automatique des rappels programmés
        print("🧪 TEST 4: Traitement automatique des rappels programmés")
        print("-" * 50)
        
        print("🚀 Lancement du traitement automatique...")
        from run_reminders_manual import process_scheduled_reminders
        result = process_scheduled_reminders()
        print(f"📊 Résultat traitement automatique: {result}")
        
        # Vérifier le statut du rappel automatique
        if 'reminder_auto' in locals():
            reminder_auto.refresh_from_db()
            print(f"📊 Statut rappel automatique après traitement: {reminder_auto.status}")
        
        print()
        
        # Résumé des tests
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        if 'reminder_manual' in locals():
            print(f"Test 1 (manuel): {reminder_manual.status} ✅" if reminder_manual.status == 'sent' else f"Test 1 (manuel): {reminder_manual.status} ❌")
        if 'reminder_auto' in locals():
            print(f"Test 2 (automatique): {reminder_auto.status} ✅" if reminder_auto.status == 'sent' else f"Test 2 (automatique): {reminder_auto.status} ❌")
        
        # Nettoyage
        print("\n🧹 Nettoyage des tests...")
        if 'reminder_manual' in locals():
            reminder_manual.delete()
        if 'reminder_auto' in locals():
            reminder_auto.delete()
        print("✅ Tests nettoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_reminder_system()
