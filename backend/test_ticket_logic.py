#!/usr/bin/env python
"""
Test de la logique des billets personnalisés vs billets par défaut
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, User, UserProfile, TicketType, EventRegistration
from django.db import transaction

def test_ticket_logic():
    """Test de la logique des billets"""
    print("🧪 Test de la logique des billets personnalisés vs billets par défaut")
    print("=" * 70)
    
    # Vérifier qu'il y a des événements
    events = Event.objects.all()
    if not events.exists():
        print("❌ Aucun événement trouvé. Créez d'abord un événement.")
        return
    
    event = events.first()
    print(f"📅 Événement testé: {event.title}")
    print(f"   Capacité: {event.place_type}, Max: {event.max_capacity}")
    print(f"   Inscriptions actuelles: {event.current_registrations}")
    print()
    
    # Vérifier les types de billets
    ticket_types = event.ticket_types.all()
    if not ticket_types.exists():
        print("❌ Aucun type de billet trouvé. Créez d'abord des types de billets.")
        return
    
    print("🎫 Types de billets disponibles:")
    for tt in ticket_types:
        confirmed_count = EventRegistration.objects.filter(
            event=event,
            ticket_type=tt,
            status__in=['confirmed', 'attended']
        ).count()
        
        print(f"   {tt.name}:")
        print(f"     Prix: ${tt.price}")
        print(f"     Quantité: {tt.quantity}")
        print(f"     Vendus: {tt.sold_count}")
        print(f"     Confirmés: {confirmed_count}")
        print(f"     Disponibles: {tt.quantity - confirmed_count if tt.quantity else 'Illimité'}")
        print()
    
    # Vérifier les inscriptions existantes
    registrations = EventRegistration.objects.filter(event=event)
    print("📋 Inscriptions existantes:")
    for reg in registrations:
        ticket_info = f" - {reg.ticket_type.name}" if reg.ticket_type else " - Par défaut"
        print(f"   {reg.user.username}: {reg.status} {ticket_info}")
    
    print()
    print("✅ Test terminé!")
    print()
    print("📝 Logique attendue:")
    print("   1. Billets personnalisés (VIP, STANDARD): Liste d'attente si épuisés")
    print("   2. Billet 'Par défaut': Liste d'attente si événement complet")
    print("   3. Prix du paiement = prix du billet sélectionné")

if __name__ == '__main__':
    test_ticket_logic()













