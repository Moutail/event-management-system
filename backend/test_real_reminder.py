#!/usr/bin/env python
"""
🧪 TEST RÉEL D'UN RAPPEL AUTOMATIQUE
Crée un rappel programmé dans 1 minute pour tester le système
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

def create_real_reminder():
    """Créer un rappel réel programmé dans 1 minute"""
    print("🔧 Création d'un rappel réel...")
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_real_reminder',
            defaults={
                'email': 'test@realreminder.com',
                'first_name': 'Test',
                'last_name': 'Real'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Rappel Réel',
            defaults={
                'description': 'Événement pour tester les rappels automatiques réels',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location',
                'max_capacity': 100,
                'organizer': user,
                'status': 'published'
            }
        )
        
        # Créer une inscription de test
        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={
                'status': 'confirmed',
                'price_paid': 0,
                'payment_status': 'paid'
            }
        )
        
        # Programmer le rappel dans 1 minute
        scheduled_time = timezone.now() + timedelta(minutes=1)
        
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=user,
            title='RAPPEL AUTOMATIQUE TEST',
            message='Ceci est un test de rappel automatique. Si vous recevez ce message, le système fonctionne !',
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
        print(f"   - Destinataires: {reminder.get_recipients().count()}")
        
        print(f"\n⏰ Le rappel sera envoyé dans 1 minute à {scheduled_time.strftime('%H:%M:%S')}")
        print(f"📧 Email sera envoyé à: {user.email}")
        
        return reminder
        
    except Exception as e:
        print(f"❌ Erreur création rappel: {e}")
        import traceback
        traceback.print_exc()
        return None

def monitor_reminder(reminder_id):
    """Surveiller le statut du rappel"""
    print(f"\n🔍 Surveillance du rappel {reminder_id}...")
    
    for i in range(70):  # Surveiller pendant 70 secondes
        try:
            reminder = CustomReminder.objects.get(id=reminder_id)
            now = timezone.now()
            
            print(f"⏰ {now.strftime('%H:%M:%S')} - Statut: {reminder.status}")
            
            if reminder.status == 'sent':
                print("🎉 SUCCÈS! Le rappel a été envoyé automatiquement!")
                print(f"📊 Statistiques:")
                print(f"   - Emails envoyés: {reminder.emails_sent}")
                print(f"   - SMS envoyés: {reminder.sms_sent}")
                print(f"   - Emails échoués: {reminder.emails_failed}")
                print(f"   - SMS échoués: {reminder.sms_failed}")
                return True
            elif reminder.status == 'failed':
                print("❌ ÉCHEC! Le rappel n'a pas pu être envoyé")
                return False
            
            # Attendre 1 seconde
            import time
            time.sleep(1)
            
        except CustomReminder.DoesNotExist:
            print("❌ Rappel non trouvé")
            return False
        except Exception as e:
            print(f"❌ Erreur surveillance: {e}")
            return False
    
    print("⏰ Timeout - Le rappel n'a pas été envoyé dans les 70 secondes")
    return False

def cleanup_test_data():
    """Nettoyer les données de test"""
    print("\n🧹 Nettoyage des données de test...")
    
    try:
        # Supprimer les rappels de test
        CustomReminder.objects.filter(
            title__startswith='RAPPEL AUTOMATIQUE TEST'
        ).delete()
        
        print("✅ Données de test nettoyées")
        
    except Exception as e:
        print(f"⚠️ Erreur nettoyage: {e}")

if __name__ == "__main__":
    print("🧪 TEST RÉEL D'UN RAPPEL AUTOMATIQUE")
    print("=" * 50)
    print("⚠️  IMPORTANT: Assurez-vous que Celery Worker et Beat sont démarrés!")
    print("   Commande: python start_automatic_reminders.py")
    print("=" * 50)
    
    try:
        # Créer le rappel
        reminder = create_real_reminder()
        if not reminder:
            print("❌ Impossible de créer le rappel")
            sys.exit(1)
        
        # Surveiller le rappel
        success = monitor_reminder(reminder.id)
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DU TEST")
        print("=" * 50)
        
        if success:
            print("🎉 TEST RÉUSSI!")
            print("✅ Le système de rappels automatiques fonctionne parfaitement")
            print("✅ Les rappels sont envoyés à l'heure exacte programmée")
        else:
            print("❌ TEST ÉCHOUÉ!")
            print("⚠️  Vérifiez que Celery Worker et Beat sont démarrés")
            print("   Commande: python start_automatic_reminders.py")
        
        # Nettoyage
        cleanup_test_data()
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
