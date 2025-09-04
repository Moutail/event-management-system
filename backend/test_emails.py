#!/usr/bin/env python
"""
Script de test pour vérifier l'envoi d'emails et la génération de QR codes
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
from django.utils import timezone

def test_email_templates():
    """Tester si les templates d'emails sont trouvés"""
    print("🔍 Test des templates d'emails...")
    
    try:
        # Test template de confirmation
        context = {
            'user': User.objects.first(),
            'event': Event.objects.first(),
            'qr_url': 'http://localhost:8000/media/qr_test.png'
        }
        
        # Rendu des templates
        html_content = render_to_string('emails/registration_confirmation.html', context)
        text_content = render_to_string('emails/registration_confirmation.txt', context)
        
        print(f"✅ Template HTML trouvé: {len(html_content)} caractères")
        print(f"✅ Template texte trouvé: {len(text_content)} caractères")
        
        return True
    except Exception as e:
        print(f"❌ Erreur template: {e}")
        return False

def test_email_sending():
    """Tester l'envoi d'emails"""
    print("\n📧 Test d'envoi d'emails...")
    
    try:
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_email_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Créer un événement de test
        event, created = Event.objects.get_or_create(
            title='Test Email Event',
            defaults={
                'description': 'Événement de test pour emails',
                'start_date': timezone.now() + timezone.timedelta(days=7),
                'end_date': timezone.now() + timezone.timedelta(days=7, hours=2),
                'location': 'Test Location',
                'price': 25.00,
                'status': 'published'
            }
        )
        
        # Créer une inscription de test
        registration, created = EventRegistration.objects.get_or_create(
            user=user,
            event=event,
            defaults={
                'status': 'confirmed',
                'payment_status': 'paid',
                'price_paid': 25.00
            }
        )
        
        print(f"✅ Utilisateur de test: {user.username}")
        print(f"✅ Événement de test: {event.title}")
        print(f"✅ Inscription de test: {registration.id}")
        
        # Test envoi email
        subject = f"Test Email - {event.title}"
        context = {
            'user': user,
            'event': event,
            'qr_url': 'http://localhost:8000/media/qr_test.png'
        }
        
        html_message = render_to_string('emails/registration_confirmation.html', context)
        text_message = render_to_string('emails/registration_confirmation.txt', context)
        
        # Envoyer l'email
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
            print("✅ Email envoyé avec succès !")
            print("📧 Vérifiez votre terminal pour voir le contenu de l'email")
        else:
            print("❌ Échec de l'envoi de l'email")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qr_generation():
    """Tester la génération de QR codes"""
    print("\n🎫 Test de génération de QR codes...")
    
    try:
        # Récupérer une inscription confirmée
        registration = EventRegistration.objects.filter(
            status='confirmed',
            payment_status='paid'
        ).first()
        
        if not registration:
            print("⚠️ Aucune inscription confirmée trouvée pour tester les QR codes")
            return False
            
        print(f"✅ Inscription trouvée: {registration.id}")
        
        # Tester la génération du QR
        if hasattr(registration, '_generate_and_store_qr'):
            try:
                registration._generate_and_store_qr()
                print("✅ QR code généré avec succès !")
                
                if registration.qr_code:
                    print(f"✅ Fichier QR: {registration.qr_code.name}")
                    print(f"✅ URL QR: {registration.qr_code.url}")
                else:
                    print("⚠️ QR code généré mais fichier non sauvegardé")
                    
            except Exception as qr_error:
                print(f"❌ Erreur génération QR: {qr_error}")
                return False
        else:
            print("❌ Méthode _generate_and_store_qr non trouvée")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur test QR: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'emails et QR codes...")
    print("=" * 50)
    
    # Test 1: Templates
    templates_ok = test_email_templates()
    
    # Test 2: Envoi d'emails
    emails_ok = test_email_sending()
    
    # Test 3: Génération QR codes
    qr_ok = test_qr_generation()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   Templates: {'✅ OK' if templates_ok else '❌ ÉCHEC'}")
    print(f"   Emails: {'✅ OK' if emails_ok else '❌ ÉCHEC'}")
    print(f"   QR Codes: {'✅ OK' if qr_ok else '❌ ÉCHEC'}")
    
    if all([templates_ok, emails_ok, qr_ok]):
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("✅ Votre système d'emails et QR codes fonctionne parfaitement !")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus et corrigez-les")

if __name__ == '__main__':
    main()


