#!/usr/bin/env python3
"""
Vérification de l'organisateur de l'événement 93
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, User

def check_organizer():
    """Vérifie qui est l'organisateur de l'événement 93"""
    print("=== VÉRIFICATION DE L'ORGANISATEUR ===\n")
    
    try:
        # 1. Récupérer l'événement 93
        try:
            event = Event.objects.get(id=93)
            print(f"✅ Événement: {event.title}")
            print(f"   ID: {event.id}")
            print(f"   Organisateur ID: {event.organizer.id}")
            print(f"   Organisateur username: {event.organizer.username}")
            print(f"   Organisateur email: {event.organizer.email}")
        except Event.DoesNotExist:
            print(f"❌ Événement 93 non trouvé")
            return
        
        print()
        
        # 2. Vérifier l'utilisateur nealdov7
        try:
            user = User.objects.get(username="nealdov7")
            print(f"✅ Utilisateur: {user.username}")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Est organisateur: {'Oui' if user.id == event.organizer.id else 'Non'}")
        except User.DoesNotExist:
            print(f"❌ Utilisateur nealdov7 non trouvé")
            return
        
        print()
        
        # 3. Vérifier l'utilisateur xchak475
        try:
            user2 = User.objects.get(username="xchak475")
            print(f"✅ Utilisateur: {user2.username}")
            print(f"   ID: {user2.id}")
            print(f"   Email: {user2.email}")
            print(f"   Est organisateur: {'Oui' if user2.id == event.organizer.id else 'Non'}")
        except User.DoesNotExist:
            print(f"❌ Utilisateur xchak475 non trouvé")
        
        print("\n=== RÉSULTAT ===")
        if user.id == event.organizer.id:
            print("✅ nealdov7 EST l'organisateur de l'événement 93")
        else:
            print("❌ nealdov7 N'EST PAS l'organisateur de l'événement 93")
            print(f"   L'organisateur est: {event.organizer.username} (ID: {event.organizer.id})")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_organizer()
