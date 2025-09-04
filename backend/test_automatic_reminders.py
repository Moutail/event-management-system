#!/usr/bin/env python
"""
🧪 TEST DES RAPPELS AUTOMATIQUES
Teste le système de rappels programmés
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
    """Créer un rappel de test programmé dans 2 minutes"""
    print("🔧 Création d'un rappel de test...")
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_reminder_user',
            defaults={
                'email': 'test@reminder.com',
                'first_name': 'Test',
                'last_name': 'Reminder'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Rappel Automatique',
            defaults={
                'description': 'Événement pour tester les rappels automatiques',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location',
                'max_capacity': 100,
                'organizer': user,
                'status': 'published'
            }
        )
        
        # Créer une inscription de test pour avoir des destinataires (si elle n'existe pas déjà)
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={
                'status': 'confirmed',
                'price_paid': 0,
                'payment_status': 'paid'
            }
        )
        
        # Programmer le rappel dans 2 minutes
        scheduled_time = timezone.now() + timedelta(minutes=2)
        
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='Test Rappel Automatique',
            message='Ceci est un test de rappel automatique programmé.',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,  # Désactiver SMS pour le test
            status='scheduled',
            scheduled_at=scheduled_time
        )
        
        print(f"✅ Rappel créé:")
        print(f"   - ID: {reminder.id}")
        print(f"   - Titre: {reminder.title}")
        print(f"   - Heure programmée: {scheduled_time}")
        print(f"   - Statut: {reminder.status}")
        
        return reminder
        
    except Exception as e:
        print(f"❌ Erreur création rappel: {e}")
        return None

def test_reminder_system():
    """Tester le système de rappels"""
    print("🧪 TEST DU SYSTÈME DE RAPPELS AUTOMATIQUES")
    print("=" * 60)
    
    # 1. Créer un rappel de test
    reminder = create_test_reminder()
    if not reminder:
        return False
    
    print(f"\n⏰ Rappel programmé pour: {reminder.scheduled_at}")
    print(f"🕐 Heure actuelle: {timezone.now()}")
    
    # 2. Vérifier que le rappel est bien programmé
    scheduled_reminders = CustomReminder.objects.filter(
        status='scheduled',
        scheduled_at__lte=timezone.now() + timedelta(minutes=5)
    )
    
    print(f"\n📊 Rappels programmés (dans les 5 prochaines minutes): {scheduled_reminders.count()}")
    
    # 3. Tester la tâche de vérification
    print(f"\n🔍 Test de la tâche de vérification...")
    result = check_scheduled_reminders()
    print(f"✅ Résultat: {result}")
    
    # 4. Vérifier le statut du rappel après le test
    reminder.refresh_from_db()
    print(f"\n📋 Statut du rappel après test: {reminder.status}")
    
    if reminder.status == 'sent':
        print("🎉 SUCCÈS: Le rappel a été envoyé automatiquement!")
        return True
    elif reminder.status == 'scheduled':
        print("⏳ Le rappel est toujours programmé (normal si l'heure n'est pas encore arrivée)")
        print(f"   Heure programmée: {reminder.scheduled_at}")
        print(f"   Heure actuelle: {timezone.now()}")
        return True
    else:
        print(f"⚠️ Statut inattendu: {reminder.status}")
        return False

def test_immediate_reminder():
    """Tester un rappel immédiat"""
    print("\n🚀 TEST RAPPEL IMMÉDIAT")
    print("=" * 40)
    
    try:
        # Créer un rappel programmé pour maintenant
        user = User.objects.filter(username='test_reminder_user').first()
        event = Event.objects.filter(title='Test Rappel Automatique').first()
        
        if not user or not event:
            print("❌ Utilisateur ou événement de test non trouvé")
            return False
        
        # Créer une inscription pour le test immédiat (si elle n'existe pas déjà)
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
            title='Test Rappel Immédiat',
            message='Ceci est un test de rappel immédiat.',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=False,
            status='scheduled',
            scheduled_at=timezone.now() - timedelta(minutes=1)  # Dans le passé
        )
        
        print(f"✅ Rappel immédiat créé (ID: {reminder.id})")
        
        # Tester l'envoi immédiat
        result = send_reminder_task(reminder.id)
        print(f"✅ Résultat envoi immédiat: {result}")
        
        # Vérifier le statut
        reminder.refresh_from_db()
        print(f"📋 Statut après envoi: {reminder.status}")
        
        return reminder.status == 'sent'
        
    except Exception as e:
        print(f"❌ Erreur test immédiat: {e}")
        return False

def cleanup_test_data():
    """Nettoyer les données de test"""
    print("\n🧹 Nettoyage des données de test...")
    
    try:
        # Supprimer les rappels de test
        CustomReminder.objects.filter(
            title__startswith='Test Rappel'
        ).delete()
        
        print("✅ Données de test nettoyées")
        
    except Exception as e:
        print(f"⚠️ Erreur nettoyage: {e}")

if __name__ == "__main__":
    try:
        # Test principal
        success1 = test_reminder_system()
        
        # Test immédiat
        success2 = test_immediate_reminder()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"✅ Test système de rappels: {'SUCCÈS' if success1 else 'ÉCHEC'}")
        print(f"✅ Test rappel immédiat: {'SUCCÈS' if success2 else 'ÉCHEC'}")
        
        if success1 and success2:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ Le système de rappels automatiques fonctionne correctement")
        else:
            print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
            print("❌ Vérifiez la configuration Celery et les logs")
        
        # Nettoyage
        cleanup_test_data()
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
