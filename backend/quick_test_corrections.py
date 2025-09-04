#!/usr/bin/env python
"""
Test rapide pour vérifier que nos corrections sont appliquées
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, TicketType, EventRegistration

def quick_test():
    """Test rapide des corrections"""
    print("🧪 Test rapide des corrections")
    print("=" * 40)
    
    # Vérifier l'événement WINNER
    try:
        event = Event.objects.get(title='WINNER')
        print(f"✅ Événement trouvé: {event.title}")
        print(f"   Capacité: {event.place_type}, Max: {event.max_capacity}")
        print(f"   Inscriptions actuelles: {event.current_registrations}")
    except Event.DoesNotExist:
        print("❌ Événement WINNER non trouvé")
        return
    
    print()
    
    # Vérifier les types de billets
    ticket_types = event.ticket_types.all()
    print(f"🎫 Types de billets ({ticket_types.count()}):")
    
    for tt in ticket_types:
        confirmed_count = EventRegistration.objects.filter(
            event=event,
            ticket_type=tt,
            status__in=['confirmed', 'attended']
        ).count()
        
        print(f"   {tt.name}:")
        print(f"     Prix: ${tt.price}")
        print(f"     Quantité: {tt.quantity}")
        print(f"     Confirmés: {confirmed_count}")
        print(f"     Disponibles: {tt.quantity - confirmed_count if tt.quantity else 'Illimité'}")
        print()
    
    # Vérifier les inscriptions existantes
    registrations = EventRegistration.objects.filter(event=event)
    print(f"📋 Inscriptions existantes ({registrations.count()}):")
    
    for reg in registrations:
        ticket_info = f" - {reg.ticket_type.name}" if reg.ticket_type else " - Par défaut"
        print(f"   {reg.user.username}: {reg.status} {ticket_info}")
    
    print()
    print("✅ Test rapide terminé!")

if __name__ == '__main__':
    quick_test()














