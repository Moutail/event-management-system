#!/usr/bin/env python3
"""
Vérification des dates de l'événement CONFER1
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event
from django.utils import timezone

def check_event_dates():
    """Vérifie les dates de l'événement CONFER1"""
    print("=== VÉRIFICATION DES DATES DE L'ÉVÉNEMENT CONFER1 ===\n")
    
    try:
        # 1. Récupérer l'événement CONFER1
        event = Event.objects.get(title="CONFER1")
        print(f"📅 Événement: {event.title}")
        print(f"   ID: {event.id}")
        print(f"   Date de début: {event.start_date}")
        print(f"   Date de fin: {event.end_date}")
        print(f"   Type: {event.event_type}")
        
        # 2. Heure actuelle
        now = timezone.now()
        print(f"\n⏰ Heure actuelle: {now}")
        
        # 3. Vérifier si l'événement est terminé
        if event.end_date:
            if now > event.end_date:
                print(f"   ❌ ÉVÉNEMENT TERMINÉ !")
                print(f"   Il y a {now - event.end_date} de retard")
            elif now < event.start_date:
                print(f"   ⏳ ÉVÉNEMENT N'A PAS ENCORE COMMENCÉ")
                print(f"   Commence dans {event.start_date - now}")
            else:
                print(f"   ✅ ÉVÉNEMENT EN COURS")
                print(f"   Se termine dans {event.end_date - now}")
        else:
            print(f"   ⚠️ Pas de date de fin définie")
        
        # 4. Vérifier les inscriptions
        print(f"\n📋 INSCRIPTIONS:")
        registrations = event.registrations.all()
        print(f"   Total: {registrations.count()}")
        
        for reg in registrations:
            print(f"   - {reg.user.username}: {reg.status} (paiement: {reg.payment_status})")
        
        # 5. Vérifier les détails virtuels
        if hasattr(event, 'virtual_details'):
            virtual = event.virtual_details
            print(f"\n🎥 DÉTAILS VIRTUELS:")
            print(f"   Meeting ID: {virtual.meeting_id}")
            print(f"   Meeting URL: {virtual.meeting_url}")
            print(f"   Meeting Password: {virtual.meeting_password}")
            print(f"   Platform: {virtual.platform}")
        else:
            print(f"\n❌ Pas de détails virtuels")
        
        print("\n=== VÉRIFICATION TERMINÉE ===")
        
    except Event.DoesNotExist:
        print(f"❌ Événement CONFER1 non trouvé")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_event_dates()
