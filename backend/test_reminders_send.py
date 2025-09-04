#!/usr/bin/env python3
"""
Script de test d'envoi direct pour le système de rappels personnalisés
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
from events.views import CustomReminderViewSet

def test_reminders_send():
    """Tester l'envoi direct des rappels personnalisés"""
    
    print("🔍 TEST D'ENVOI DIRECT DU SYSTÈME DE RAPPELS PERSONNALISÉS")
    print("=" * 70)
    
    # 1. Récupérer l'organisateur de test
    print("\n1. Récupération de l'organisateur de test...")
    try:
        organizer = User.objects.get(username='organizer_test')
        print(f"✅ Organisateur trouvé: {organizer.username} (ID: {organizer.id})")
    except User.DoesNotExist:
        print("❌ Organisateur de test non trouvé")
        return
    
    # 2. Récupérer l'événement de test
    print("\n2. Récupération de l'événement de test...")
    try:
        event = Event.objects.get(title="Événement Test Rappels")
        print(f"✅ Événement trouvé: {event.title} (ID: {event.id})")
    except Event.DoesNotExist:
        print("❌ Événement de test non trouvé")
        return
    
    # 3. Créer un rappel de test
    print("\n3. Création d'un rappel de test...")
    try:
        reminder = CustomReminder.objects.create(
            event=event,
            created_by=organizer,
            title='Test Envoi Direct',
            message='Ceci est un test d\'envoi direct de rappel personnalisé.',
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
    
    # 4. Tester l'envoi direct
    print("\n4. Test d'envoi direct du rappel...")
    try:
        # Créer une instance de la vue pour accéder aux méthodes privées
        viewset = CustomReminderViewSet()
        
        # Simuler une requête
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        viewset.request = MockRequest(organizer)
        
        # Appeler la méthode d'envoi
        print("🔍 Début de l'envoi du rappel...")
        result = viewset._send_reminder(reminder)
        
        if result['success']:
            print("✅ Rappel envoyé avec succès!")
            print(f"   Statistiques: {result['statistics']}")
            
            # Mettre à jour le statut
            reminder.mark_as_sent()
            print("✅ Rappel marqué comme envoyé")
        else:
            print(f"❌ Erreur lors de l'envoi: {result.get('error', 'Erreur inconnue')}")
        
    except Exception as e:
        print(f"❌ Erreur test envoi: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Afficher les détails des destinataires
    print("\n5. Détails des destinataires...")
    try:
        recipients = reminder.get_recipients()
        print(f"✅ {recipients.count()} destinataire(s):")
        
        for recipient in recipients:
            if recipient.user:
                print(f"   - Utilisateur: {recipient.user.username}")
                print(f"     Email: {recipient.user.email}")
                if hasattr(recipient.user, 'profile') and recipient.user.profile.phone:
                    print(f"     Téléphone: {recipient.user.profile.phone}")
                    print(f"     Pays: {recipient.user.profile.country}")
                else:
                    print(f"     Téléphone: Non défini")
            else:
                print(f"   - Invité: {recipient.guest_full_name}")
                print(f"     Email: {recipient.guest_email}")
                print(f"     Téléphone: {recipient.guest_phone}")
                print(f"     Pays: {recipient.guest_country}")
        
    except Exception as e:
        print(f"❌ Erreur détails destinataires: {e}")
    
    # 6. Tester l'envoi d'email individuel
    print("\n6. Test d'envoi d'email individuel...")
    try:
        viewset = CustomReminderViewSet()
        
        # Récupérer le premier destinataire
        recipients = reminder.get_recipients()
        if recipients.exists():
            recipient = recipients.first()
            
            print(f"🔍 Test envoi email à: {recipient.user.email if recipient.user else recipient.guest_email}")
            
            # Tester l'envoi d'email
            email_sent = viewset._send_reminder_email(reminder, recipient)
            
            if email_sent:
                print("✅ Email envoyé avec succès!")
            else:
                print("❌ Échec envoi email")
        else:
            print("❌ Aucun destinataire trouvé")
        
    except Exception as e:
        print(f"❌ Erreur test email: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Tester l'envoi SMS individuel
    print("\n7. Test d'envoi SMS individuel...")
    try:
        viewset = CustomReminderViewSet()
        
        # Récupérer le premier destinataire
        recipients = reminder.get_recipients()
        if recipients.exists():
            recipient = recipients.first()
            
            # Déterminer le numéro de téléphone
            if recipient.user and hasattr(recipient.user, 'profile') and recipient.user.profile.phone:
                phone = recipient.user.profile.phone
                country = recipient.user.profile.country or 'FR'
            elif recipient.guest_phone:
                phone = recipient.guest_phone
                country = recipient.guest_country or 'FR'
            else:
                phone = None
            
            if phone:
                print(f"🔍 Test envoi SMS à: {phone} ({country})")
                
                # Tester l'envoi SMS
                sms_sent = viewset._send_reminder_sms(reminder, recipient)
                
                if sms_sent:
                    print("✅ SMS envoyé avec succès!")
                else:
                    print("❌ Échec envoi SMS")
            else:
                print("❌ Aucun numéro de téléphone trouvé")
        else:
            print("❌ Aucun destinataire trouvé")
        
    except Exception as e:
        print(f"❌ Erreur test SMS: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 TEST D'ENVOI DIRECT TERMINÉ!")
    print("Vérifiez les logs du serveur pour voir les détails d'envoi.")
    print("Vérifiez votre boîte email et votre téléphone pour les messages.")

if __name__ == "__main__":
    test_reminders_send()


