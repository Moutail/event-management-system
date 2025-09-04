#!/usr/bin/env python3
"""
Test simple du système de mails
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent, EventRegistration
from events.emails import send_event_confirmation_email

def test_mail_simple():
    """Test simple du système de mails"""
    print("=== TEST SIMPLE DU SYSTEME DE MAILS ===\n")
    
    try:
        # 1. Vérifier l'événement CONFEMMA2
        print("1. Vérification de l'événement CONFEMMA2...")
        event = Event.objects.get(title="CONFEMMA2")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Type: {event.event_type}")
        
        # 2. Vérifier le VirtualEvent
        print(f"\n2. Vérification du VirtualEvent...")
        try:
            virtual_event = event.virtual_details
            print(f"   ✅ VirtualEvent trouvé: ID {virtual_event.id}")
            print(f"   Platform: {virtual_event.platform}")
            print(f"   Meeting ID: {virtual_event.meeting_id}")
            print(f"   Meeting URL: {virtual_event.meeting_url}")
            print(f"   Meeting Password: {virtual_event.meeting_password}")
        except VirtualEvent.DoesNotExist:
            print(f"   ❌ Aucun VirtualEvent configuré")
            return
        
        # 3. Vérifier les inscriptions
        print(f"\n3. Vérification des inscriptions...")
        registrations = EventRegistration.objects.filter(event=event)
        print(f"   Total inscriptions: {registrations.count()}")
        
        for reg in registrations:
            print(f"   - {reg.user.username}: {reg.status}")
            print(f"     Email: {reg.user.email}")
        
        # 4. Tester l'envoi de mail
        print(f"\n4. Test de l'envoi de mail...")
        
        # Trouver une inscription confirmée
        confirmed_reg = registrations.filter(status='confirmed').first()
        if confirmed_reg:
            print(f"   Test avec l'inscription de {confirmed_reg.user.username}")
            print(f"   Email: {confirmed_reg.user.email}")
            
            try:
                # Tester l'envoi du mail
                result = send_event_confirmation_email(confirmed_reg)
                print(f"   ✅ Mail envoyé avec succès: {result}")
            except Exception as e:
                print(f"   ❌ Erreur envoi mail: {e}")
        else:
            print(f"   ⚠️ Aucune inscription confirmée trouvée pour tester")
        
        print("\n=== TEST TERMINE ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mail_simple()
