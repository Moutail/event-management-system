#!/usr/bin/env python3
"""
Vérification du statut de l'utilisateur xchak475
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, User

def check_user_status():
    """Vérifie le statut de l'utilisateur xchak475"""
    print("=== VÉRIFICATION DU STATUT DE XCHAK475 ===\n")
    
    try:
        # 1. Récupérer l'utilisateur xchak475
        try:
            user = User.objects.get(username="xchak475")
            print(f"✅ Utilisateur: {user.username}")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
        except User.DoesNotExist:
            print(f"❌ Utilisateur xchak475 non trouvé")
            return
        
        print()
        
        # 2. Vérifier l'événement 93
        try:
            event = Event.objects.get(id=93)
            print(f"✅ Événement: {event.title}")
            print(f"   ID: {event.id}")
            print(f"   Organisateur: {event.organizer.username}")
        except Event.DoesNotExist:
            print(f"❌ Événement 93 non trouvé")
            return
        
        print()
        
        # 3. Vérifier les inscriptions de xchak475 pour l'événement 93
        registrations = EventRegistration.objects.filter(
            event=event,
            user=user
        )
        
        print(f"📋 Inscriptions de {user.username} pour l'événement {event.id}:")
        if registrations.exists():
            for reg in registrations:
                print(f"   - ID: {reg.id}")
                print(f"     Status: {reg.status}")
                print(f"     Payment Status: {reg.payment_status}")
                print(f"     Price Paid: {reg.price_paid}")
                print(f"     Created: {reg.created_at}")
                print(f"     Updated: {reg.updated_at}")
                print()
        else:
            print(f"   ❌ Aucune inscription trouvée")
        
        # 4. Vérifier si xchak475 a une inscription confirmée ET payée
        confirmed_paid = registrations.filter(
            status='confirmed',
            payment_status='paid'
        )
        
        if confirmed_paid.exists():
            print(f"✅ {user.username} a une inscription confirmée ET payée !")
            print(f"   C'est pourquoi il peut accéder au stream")
        else:
            print(f"❌ {user.username} n'a pas d'inscription confirmée ET payée")
            print(f"   Il ne devrait pas pouvoir accéder au stream")
        
        print("\n=== RÉSULTAT ===")
        print("🔍 Vérification du statut de paiement de xchak475")
        print("💰 Si payment_status = 'paid', il peut accéder au stream")
        print("🚫 Si payment_status ≠ 'paid', il devrait être bloqué")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_status()


