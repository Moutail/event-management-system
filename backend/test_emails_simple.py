#!/usr/bin/env python
"""
Script de test simplifié pour vérifier l'envoi d'emails
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from events.models import Event, EventRegistration, User

def test_email_with_existing_data():
    """Tester l'envoi d'emails avec les données existantes"""
    print("🔍 Test des emails avec données existantes...")
    
    try:
        # Récupérer un utilisateur existant
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé dans la base")
            return False
            
        print(f"✅ Utilisateur trouvé: {user.username} ({user.email})")
        
        # Récupérer un événement existant
        event = Event.objects.first()
        if not event:
            print("❌ Aucun événement trouvé dans la base")
            return False
            
        print(f"✅ Événement trouvé: {event.title}")
        
        # Récupérer une inscription existante
        registration = EventRegistration.objects.filter(
            user=user,
            event=event
        ).first()
        
        if not registration:
            print("❌ Aucune inscription trouvée pour cet utilisateur et événement")
            return False
            
        print(f"✅ Inscription trouvée: {registration.id} (statut: {registration.status})")
        
        # Test envoi email de confirmation
        print("\n📧 Test envoi email de confirmation...")
        
        context = {
            'user': user,
            'event': event,
            'qr_url': 'http://localhost:8000/media/qr_test.png'
        }
        
        html_message = render_to_string('emails/registration_confirmation.html', context)
        text_message = render_to_string('emails/registration_confirmation.txt', context)
        
        subject = f"Test Email - Confirmation {event.title}"
        
        msg = EmailMultiAlternatives(
            subject, 
            text_message, 
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@test.com'),
            [user.email]
        )
        msg.attach_alternative(html_message, 'text/html')
        
        # En mode console, l'email sera affiché dans le terminal
        result = msg.send(fail_silently=False)
        
        if result:
            print("✅ Email de confirmation envoyé avec succès !")
            print("📧 Vérifiez votre terminal pour voir le contenu de l'email")
        else:
            print("❌ Échec de l'envoi de l'email de confirmation")
            
        # Test envoi email de liste d'attente
        print("\n📧 Test envoi email de liste d'attente...")
        
        context_waitlist = {
            'user': user,
            'event': event
        }
        
        html_waitlist = render_to_string('emails/registration_waitlisted.html', context_waitlist)
        text_waitlist = render_to_string('emails/registration_waitlisted.txt', context_waitlist)
        
        subject_waitlist = f"Test Email - Liste d'attente {event.title}"
        
        msg_waitlist = EmailMultiAlternatives(
            subject_waitlist, 
            text_waitlist, 
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@test.com'),
            [user.email]
        )
        msg_waitlist.attach_alternative(html_waitlist, 'text/html')
        
        result_waitlist = msg_waitlist.send(fail_silently=False)
        
        if result_waitlist:
            print("✅ Email de liste d'attente envoyé avec succès !")
        else:
            print("❌ Échec de l'envoi de l'email de liste d'attente")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur test emails: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des emails avec données existantes...")
    print("=" * 50)
    
    success = test_email_with_existing_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST RÉUSSI !")
        print("✅ Votre système d'emails fonctionne parfaitement !")
        print("📧 Vérifiez votre terminal pour voir les emails envoyés")
    else:
        print("❌ TEST ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")

if __name__ == '__main__':
    main()


