#!/usr/bin/env python3
"""
Test simple de la sécurité du streaming
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, User
from events.streaming_views import _verify_payment_access

def test_simple_security():
    """Test simple de la sécurité"""
    print("=== TEST SIMPLE DE SÉCURITÉ ===\n")
    
    try:
        # 1. Récupérer l'événement
        event = Event.objects.get(title="CONFER1")
        print(f"✅ Événement: {event.title}")
        
        # 2. Test utilisateur payé
        user_paid = User.objects.get(username="nealdov7")
        result_paid = _verify_payment_access(user_paid, event)
        print(f"🔒 Utilisateur payé ({user_paid.username}): {'✅ AUTORISÉ' if result_paid else '❌ REFUSÉ'}")
        
        # 3. Test utilisateur non inscrit
        user_not_registered = User.objects.get(username="xchak475")
        result_not_registered = _verify_payment_access(user_not_registered, event)
        print(f"🚫 Utilisateur non inscrit ({user_not_registered.username}): {'❌ AUTORISÉ (BRÈCHE!)' if result_not_registered else '✅ REFUSÉ (SÉCURISÉ)'}")
        
        # 4. Résumé
        print(f"\n🎯 RÉSUMÉ:")
        if result_paid and not result_not_registered:
            print("🎉 SÉCURISATION PARFAITE !")
        else:
            print("🚨 PROBLÈME DE SÉCURITÉ !")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")

if __name__ == "__main__":
    test_simple_security()
