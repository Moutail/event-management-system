#!/usr/bin/env python3
"""
Test du système de sécurité renforcé
"""

import os
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent, EventRegistration
from django.contrib.auth.models import User
from django.utils import timezone

def test_security_system():
    """Test du système de sécurité renforcé"""
    print("=== TEST DU SYSTEME DE SECURITE RENFORCE ===\n")
    
    try:
        # 1. Vérifier l'événement CONFEMMA2
        print("1. Vérification de l'événement CONFEMMA2...")
        event = Event.objects.get(title="CONFEMMA2")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Organisateur: {event.organizer.username}")
        
        # 2. Vérifier les inscriptions
        print(f"\n2. Vérification des inscriptions...")
        registrations = EventRegistration.objects.filter(event=event)
        print(f"   Total inscriptions: {registrations.count()}")
        
        for reg in registrations:
            print(f"   - {reg.user.username}: {reg.status} (créé: {reg.created_at})")
        
        # 3. Tester différents scénarios d'accès
        print(f"\n3. Test des scénarios d'accès...")
        
        # Scénario 1: Utilisateur non inscrit
        print(f"\n   Scénario 1: Utilisateur non inscrit")
        non_registered_user = User.objects.filter(username__startswith='test').first()
        if non_registered_user:
            print(f"   Utilisateur test: {non_registered_user.username}")
            non_reg_reg = EventRegistration.objects.filter(event=event, user=non_registered_user).first()
            if non_reg_reg:
                print(f"   Status: {non_reg_reg.status}")
            else:
                print(f"   Pas d'inscription")
        
        # Scénario 2: Utilisateur avec inscription annulée
        print(f"\n   Scénario 2: Inscription annulée")
        cancelled_regs = registrations.filter(status='cancelled')
        if cancelled_regs.exists():
            cancelled_reg = cancelled_regs.first()
            print(f"   Utilisateur: {cancelled_reg.user.username}")
            print(f"   Status: {cancelled_reg.status}")
            print(f"   Date annulation: {cancelled_reg.updated_at}")
        else:
            print(f"   Aucune inscription annulée trouvée")
        
        # Scénario 3: Utilisateur confirmé
        print(f"\n   Scénario 3: Inscription confirmée")
        confirmed_regs = registrations.filter(status='confirmed')
        if confirmed_regs.exists():
            confirmed_reg = confirmed_regs.first()
            print(f"   Utilisateur: {confirmed_reg.user.username}")
            print(f"   Status: {confirmed_reg.status}")
            print(f"   Date confirmation: {confirmed_reg.updated_at}")
        else:
            print(f"   Aucune inscription confirmée trouvée")
        
        # 4. Vérifier les méthodes de validation
        print(f"\n4. Test des validations d'événement...")
        print(f"   Streaming accessible: {event.is_streaming_accessible()}")
        print(f"   Inscriptions ouvertes: {event.is_registration_open()}")
        print(f"   Statut: {event.get_registration_status()}")
        
        print("\n=== TESTS TERMINES ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_security_system()
