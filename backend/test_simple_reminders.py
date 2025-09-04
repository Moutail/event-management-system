#!/usr/bin/env python
"""
🧪 TEST SIMPLE DES RAPPELS AUTOMATIQUES
Teste le système de rappels avec une approche directe
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
from events.tasks import check_scheduled_reminders, send_reminder_task

def create_test_reminder():
    """Créer un rappel de test programmé pour maintenant"""
    print("🔧 Création d'un rappel de test...")
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_simple_reminder',
            defaults={
                'email': 'test@simplereminder.com',
                'first_name': 'Test',
                'last_name': 'Simple'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Rappel Simple',
            defaults={
                'description': 'Événement pour tester les rappels simples',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location',
                'max_capacity': 100,
                'price': 0,
                'organizer': user,
                'status': 'published'
            }
        )
        
        # Créer une inscription pour avoir des destinataires
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={
                'status': 'confirmed',
                'price_paid': 0,
                'payment_status': 'paid'
            }
        )
        
        # Programmer le rappel pour maintenant
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Rappel Simple',
            message='Ceci est un test de rappel simple programmé pour maintenant.',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,  # Désactiver SMS pour le test
            status='scheduled',
            scheduled_at=timezone.now() - timedelta(minutes=1)  # Dans le passé
        )
        
        print(f"✅ Rappel créé:")
        print(f"   - ID: {reminder.id}")
        print(f"   - Titre: {reminder.title}")
        print(f"   - Heure programmée: {reminder.scheduled_at}")
        print(f"   - Statut: {reminder.status}")
        print(f"   - Destinataires: {registration.id}")
        
        return reminder
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du rappel: {e}")
        return None

def test_reminder_system():
    """Tester le système de rappels"""
    print("🧪 TEST DU SYSTÈME DE RAPPELS AUTOMATIQUES")
    print("=" * 60)
    
    # Créer un rappel de test
    reminder = create_test_reminder()
    if not reminder:
        return False
    
    print(f"\n🔍 Test de la fonction check_scheduled_reminders...")
    
    try:
        # Appeler directement la fonction de vérification
        result = check_scheduled_reminders()
        print(f"✅ Fonction check_scheduled_reminders exécutée: {result}")
        
        # Vérifier le statut du rappel
        reminder.refresh_from_db()
        print(f"📊 Statut du rappel après vérification: {reminder.status}")
        
        if reminder.status == 'sent':
            print("🎉 SUCCÈS! Le rappel a été envoyé automatiquement!")
            return True
        else:
            print("⚠️ Le rappel n'a pas été envoyé. Statut:", reminder.status)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_direct_send():
    """Tester l'envoi direct d'un rappel"""
    print("\n🔍 Test de l'envoi direct...")
    
    try:
        # Créer un rappel pour l'envoi direct
        user = User.objects.get(username='test_simple_reminder')
        event = Event.objects.get(title='Test Rappel Simple')
        
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Envoi Direct',
            message='Ceci est un test d\'envoi direct.',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            status='draft'
        )
        
        print(f"✅ Rappel créé pour envoi direct (ID: {reminder.id})")
        
        # Envoyer directement
        result = send_reminder_task(reminder.id)
        print(f"✅ Envoi direct exécuté: {result}")
        
        # Vérifier le statut
        reminder.refresh_from_db()
        print(f"📊 Statut après envoi direct: {reminder.status}")
        
        if reminder.status == 'sent':
            print("🎉 SUCCÈS! L'envoi direct fonctionne!")
            return True
        else:
            print("⚠️ L'envoi direct a échoué. Statut:", reminder.status)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi direct: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU TEST SIMPLE")
    print("=" * 60)
    
    # Test 1: Système automatique
    success1 = test_reminder_system()
    
    # Test 2: Envoi direct
    success2 = test_direct_send()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS:")
    print(f"   - Test automatique: {'✅ SUCCÈS' if success1 else '❌ ÉCHEC'}")
    print(f"   - Test envoi direct: {'✅ SUCCÈS' if success2 else '❌ ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le système de rappels fonctionne correctement!")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez la configuration et les logs")
    
    print("=" * 60)
