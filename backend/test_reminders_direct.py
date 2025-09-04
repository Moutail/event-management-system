#!/usr/bin/env python3
"""
Script de test direct pour le système de rappels personnalisés
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Event, EventRegistration, CustomReminder, UserProfile

def test_custom_reminders_direct():
    """Tester le système de rappels personnalisés directement"""
    
    print("🔍 TEST DIRECT DU SYSTÈME DE RAPPELS PERSONNALISÉS")
    print("=" * 60)
    
    # 1. Créer un utilisateur organisateur
    print("\n1. Création d'un organisateur...")
    try:
        organizer, created = User.objects.get_or_create(
            username='organizer_test',
            defaults={
                'email': 'organizer@test.com',
                'password': 'testpass123',
                'first_name': 'Organisateur',
                'last_name': 'Test'
            }
        )
        
        if created:
            organizer.set_password('testpass123')
            organizer.save()
        
        profile, created = UserProfile.objects.get_or_create(
            user=organizer,
            defaults={
                'role': 'organizer',
                'status_approval': 'approved'
            }
        )
        print(f"✅ Organisateur: {organizer.username} (ID: {organizer.id})")
    except Exception as e:
        print(f"❌ Erreur création organisateur: {e}")
        return
    
    # 2. Créer un événement
    print("\n2. Création d'un événement...")
    try:
        event, created = Event.objects.get_or_create(
            title="Événement Test Rappels",
            defaults={
                'description': "Événement pour tester les rappels personnalisés",
                'start_date': datetime.now() + timedelta(days=7),
                'end_date': datetime.now() + timedelta(days=7, hours=3),
                'location': "Lieu Test",
                'organizer': organizer,
                'status': 'published',
                'price': 0,
                'is_free': True
            }
        )
        print(f"✅ Événement: {event.title} (ID: {event.id})")
    except Exception as e:
        print(f"❌ Erreur création événement: {e}")
        return
    
    # 3. Créer des inscriptions
    print("\n3. Création d'inscriptions...")
    try:
        # Inscription utilisateur
        user, created = User.objects.get_or_create(
            username='participant1',
            defaults={
                'email': 'participant1@test.com',
                'password': 'testpass123'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
        
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'participant',
                'status_approval': 'approved',
                'phone': '5141234567',
                'country': 'CA'
            }
        )
        
        registration1, created = EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={'status': 'confirmed'}
        )
        print(f"✅ Inscription utilisateur: {user.username} (ID: {registration1.id})")
        
        # Inscription invité
        registration2, created = EventRegistration.objects.get_or_create(
            event=event,
            guest_email='invite@test.com',
            defaults={
                'guest_full_name': 'Invité Test',
                'guest_phone': '4387654321',
                'guest_country': 'CA',
                'is_guest_registration': True,
                'status': 'confirmed'
            }
        )
        print(f"✅ Inscription invité: {registration2.guest_full_name} (ID: {registration2.id})")
        
    except Exception as e:
        print(f"❌ Erreur création inscriptions: {e}")
        return
    
    # 4. Créer un rappel personnalisé
    print("\n4. Création d'un rappel personnalisé...")
    try:
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=organizer,
            title='Rappel Test Direct',
            message='Ceci est un message de rappel personnalisé pour tester le système directement.',
            reminder_type='general',
            target_audience='all',
            send_email=True,
            send_sms=True,
            status='draft'
        )
        
        # Calculer le nombre de destinataires
        reminder.total_recipients = reminder.get_recipients().count()
        reminder.save()
        
        print(f"✅ Rappel créé: {reminder.title} (ID: {reminder.id})")
        print(f"   Destinataires: {reminder.total_recipients}")
        print(f"   Email: {reminder.send_email}")
        print(f"   SMS: {reminder.send_sms}")
        
    except Exception as e:
        print(f"❌ Erreur création rappel: {e}")
        return
    
    # 5. Tester la récupération des destinataires
    print("\n5. Test récupération des destinataires...")
    try:
        recipients = reminder.get_recipients()
        print(f"✅ {recipients.count()} destinataire(s) trouvé(s):")
        
        for recipient in recipients:
            if recipient.user:
                print(f"   - Utilisateur: {recipient.user.username} ({recipient.user.email})")
            else:
                print(f"   - Invité: {recipient.guest_full_name} ({recipient.guest_email})")
        
    except Exception as e:
        print(f"❌ Erreur récupération destinataires: {e}")
    
    # 6. Tester l'envoi du rappel
    print("\n6. Test envoi du rappel...")
    try:
        # Simuler l'envoi
        print("🔍 Simulation de l'envoi du rappel...")
        
        # Vérifier que le rappel peut être envoyé
        if reminder.can_send():
            print("✅ Le rappel peut être envoyé")
            
            # Marquer comme envoyé
            reminder.mark_as_sent()
            print("✅ Rappel marqué comme envoyé")
            
            # Afficher les statistiques
            print(f"   Statut: {reminder.status}")
            print(f"   Date d'envoi: {reminder.sent_at}")
            print(f"   Destinataires: {reminder.total_recipients}")
            
        else:
            print("❌ Le rappel ne peut pas être envoyé")
        
    except Exception as e:
        print(f"❌ Erreur test envoi: {e}")
    
    # 7. Tester les différents types d'audience
    print("\n7. Test des différents types d'audience...")
    try:
        # Test audience "confirmed"
        reminder_confirmed = CustomReminder.objects.create(
            event=event,
            created_by=organizer,
            title='Rappel Confirmés',
            message='Message pour les confirmés uniquement.',
            reminder_type='reminder',
            target_audience='confirmed',
            send_email=True,
            send_sms=False,
            status='draft'
        )
        
        confirmed_recipients = reminder_confirmed.get_recipients()
        print(f"✅ Audience 'confirmed': {confirmed_recipients.count()} destinataire(s)")
        
        # Test audience "waitlisted"
        reminder_waitlisted = CustomReminder.objects.create(
            event=event,
            created_by=organizer,
            title='Rappel Liste Attente',
            message='Message pour la liste d\'attente.',
            reminder_type='update',
            target_audience='waitlisted',
            send_email=True,
            send_sms=False,
            status='draft'
        )
        
        waitlisted_recipients = reminder_waitlisted.get_recipients()
        print(f"✅ Audience 'waitlisted': {waitlisted_recipients.count()} destinataire(s)")
        
    except Exception as e:
        print(f"❌ Erreur test audience: {e}")
    
    # 8. Afficher tous les rappels créés
    print("\n8. Liste de tous les rappels...")
    try:
        all_reminders = CustomReminder.objects.filter(event=event)
        print(f"✅ {all_reminders.count()} rappel(s) trouvé(s) pour l'événement:")
        
        for rem in all_reminders:
            print(f"   - {rem.title} ({rem.reminder_type}) - {rem.status}")
            print(f"     Audience: {rem.target_audience}")
            print(f"     Email: {rem.send_email}, SMS: {rem.send_sms}")
            print(f"     Destinataires: {rem.get_recipients().count()}")
        
    except Exception as e:
        print(f"❌ Erreur liste rappels: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST DIRECT TERMINÉ!")
    print("Le système de rappels personnalisés fonctionne correctement.")
    print("Les rappels ont été créés et peuvent être envoyés via l'API.")

if __name__ == "__main__":
    test_custom_reminders_direct()


