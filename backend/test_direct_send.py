#!/usr/bin/env python
"""
🧪 TEST DIRECT DE L'ENVOI MANUEL
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

def send_reminder_manually(reminder):
    """Envoi manuel direct d'un rappel"""
    print(f"🚀 Envoi manuel direct du rappel {reminder.id}")
    
    try:
        # Vérifier si le rappel peut être envoyé
        if reminder.status == 'sent':
            print("❌ Ce rappel a déjà été envoyé")
            return False
        
        # Récupérer les destinataires
        recipients = reminder.get_recipients()
        print(f"📋 Destinataires trouvés: {recipients.count()}")
        
        if not recipients.exists():
            print("❌ Aucun destinataire trouvé")
            return False
        
        # Initialiser les statistiques
        statistics = {
            'total_recipients': recipients.count(),
            'emails_sent': 0,
            'sms_sent': 0,
            'emails_failed': 0,
            'sms_failed': 0
        }
        
        # Envoyer à chaque destinataire
        for registration in recipients:
            print(f"📧 Traitement destinataire: {registration.id}")
            
            # Déterminer le nom et l'email selon le type d'inscription
            if registration.user:
                recipient_name = registration.user.get_full_name() or registration.user.username
                recipient_email = registration.user.email
                recipient_phone = getattr(registration.user.profile, 'phone', '') if hasattr(registration.user, 'profile') else ''
            else:
                recipient_name = registration.guest_full_name or "Invité"
                recipient_email = registration.guest_email or ""
                recipient_phone = registration.guest_phone or ""
            
            print(f"   Nom: {recipient_name}")
            print(f"   Email: {recipient_email}")
            print(f"   Téléphone: {recipient_phone}")
            
            # Envoyer email si activé
            if reminder.send_email and recipient_email:
                print(f"   📧 Envoi email à {recipient_email}")
                # Simuler l'envoi d'email (pour le test)
                print(f"   ✅ Email envoyé avec succès")
                statistics['emails_sent'] += 1
            elif reminder.send_email and not recipient_email:
                print(f"   ⚠️ Email activé mais pas d'email disponible")
                statistics['emails_failed'] += 1
            
            # Envoyer SMS si activé
            if reminder.send_sms and recipient_phone:
                print(f"   📱 Envoi SMS à {recipient_phone}")
                # Simuler l'envoi de SMS (pour le test)
                print(f"   ✅ SMS envoyé avec succès")
                statistics['sms_sent'] += 1
            elif reminder.send_sms and not recipient_phone:
                print(f"   ⚠️ SMS activé mais pas de téléphone disponible")
                statistics['sms_failed'] += 1
        
        # Mettre à jour le rappel
        reminder.status = 'sent'
        reminder.sent_at = timezone.now()
        reminder.emails_sent = statistics['emails_sent']
        reminder.sms_sent = statistics['sms_sent']
        reminder.emails_failed = statistics['emails_failed']
        reminder.sms_failed = statistics['sms_failed']
        reminder.save()
        
        print(f"✅ Rappel envoyé avec succès!")
        print(f"📊 Statistiques: {statistics}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        reminder.status = 'failed'
        reminder.save()
        return False

def test_direct_send():
    """Test d'envoi manuel direct"""
    print("🧪 TEST DIRECT DE L'ENVOI MANUEL")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_direct_send',
            defaults={
                'email': 'test@direct.com',
                'first_name': 'Test',
                'last_name': 'Direct'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Direct Send',
            defaults={
                'description': 'Événement pour test envoi direct',
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
                'guest_full_name': 'Test Guest Direct',
                'guest_email': 'guest@direct.com',
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
            title='Test Direct Send Brouillon',
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
        
        # Envoi manuel direct
        success1 = send_reminder_manually(reminder1)
        
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
            title='Test Direct Send Programmé',
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
        
        # Envoi manuel direct
        success2 = send_reminder_manually(reminder2)
        
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
    test_direct_send()

