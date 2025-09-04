#!/usr/bin/env python
"""
Script de test final pour vérifier l'envoi d'emails
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

def test_email_final():
    """Test final des emails avec données existantes"""
    print("🔍 Test final des emails...")
    
    try:
        # Utiliser l'inscription recommandée
        registration = EventRegistration.objects.get(id=11)  # nealdov7 -> DOV12
        user = registration.user
        event = registration.event
        
        print(f"✅ Utilisateur: {user.username} ({user.email})")
        print(f"✅ Événement: {event.title}")
        print(f"✅ Inscription: {registration.id} (statut: {registration.status})")
        
        # Test 1: Email de confirmation
        print("\n📧 Test 1: Email de confirmation...")
        
        context = {
            'user': user,
            'event': event,
            'qr_url': 'http://localhost:8000/media/qr_test.png'
        }
        
        html_message = render_to_string('emails/registration_confirmation.html', context)
        text_message = render_to_string('emails/registration_confirmation.html', context)
        
        subject = f"🎉 Confirmation d'inscription - {event.title}"
        
        msg = EmailMultiAlternatives(
            subject, 
            text_message, 
            'noreply@eventmanagement.com',
            [user.email]
        )
        msg.attach_alternative(html_message, 'text/html')
        
        result = msg.send(fail_silently=False)
        
        if result:
            print("✅ Email de confirmation envoyé !")
        else:
            print("❌ Échec email de confirmation")
            
        # Test 2: Email de liste d'attente
        print("\n📧 Test 2: Email de liste d'attente...")
        
        context_waitlist = {
            'user': user,
            'event': event
        }
        
        html_waitlist = render_to_string('emails/registration_waitlisted.html', context_waitlist)
        text_waitlist = render_to_string('emails/registration_waitlisted.txt', context_waitlist)
        
        subject_waitlist = f"⏳ Inscription en attente - {event.title}"
        
        msg_waitlist = EmailMultiAlternatives(
            subject_waitlist, 
            text_waitlist, 
            'noreply@eventmanagement.com',
            [user.email]
        )
        msg_waitlist.attach_alternative(html_waitlist, 'text/html')
        
        result_waitlist = msg_waitlist.send(fail_silently=False)
        
        if result_waitlist:
            print("✅ Email de liste d'attente envoyé !")
        else:
            print("❌ Échec email de liste d'attente")
            
        print("\n🎉 TOUS LES TESTS TERMINÉS !")
        print("📧 Vérifiez votre terminal pour voir les emails")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Test final des emails...")
    print("=" * 50)
    
    success = test_email_final()
    
    if success:
        print("\n✅ TEST RÉUSSI !")
        print("🎉 Votre système d'emails fonctionne !")
    else:
        print("\n❌ TEST ÉCHOUÉ")


