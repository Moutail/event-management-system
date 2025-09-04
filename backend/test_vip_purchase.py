#!/usr/bin/env python
"""
Test de l'achat d'un billet VIP pour vérifier la logique
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, User, UserProfile, TicketType, EventRegistration
from django.db import transaction

def test_vip_purchase():
    """Test de l'achat d'un billet VIP"""
    print("🧪 Test de l'achat d'un billet VIP")
    print("=" * 50)
    
    # Trouver l'événement WINNER
    try:
        event = Event.objects.get(title='WINNER')
    except Event.DoesNotExist:
        print("❌ Événement WINNER non trouvé")
        return
    
    print(f"📅 Événement: {event.title}")
    print(f"   Capacité: {event.place_type}, Max: {event.max_capacity}")
    print(f"   Inscriptions actuelles: {event.current_registrations}")
    print()
    
    # Trouver le billet VIP
    try:
        vip_ticket = TicketType.objects.get(event=event, name='VIP')
    except TicketType.DoesNotExist:
        print("❌ Billet VIP non trouvé")
        return
    
    print(f"🎫 Billet VIP:")
    print(f"   Prix: ${vip_ticket.price}")
    print(f"   Quantité: {vip_ticket.quantity}")
    print(f"   Vendus: {vip_ticket.sold_count}")
    
    # Compter les inscriptions confirmées pour ce billet
    confirmed_count = EventRegistration.objects.filter(
        event=event,
        ticket_type=vip_ticket,
        status__in=['confirmed', 'attended']
    ).count()
    
    print(f"   Confirmés: {confirmed_count}")
    print(f"   Disponibles: {vip_ticket.quantity - confirmed_count}")
    print()
    
    # Vérifier si le billet est épuisé
    if confirmed_count >= vip_ticket.quantity:
        print("🔴 BILLET VIP ÉPUISÉ - Doit aller en liste d'attente")
        print("   Logique: L'inscription sera automatiquement mise en liste d'attente")
    else:
        print("🟢 BILLET VIP DISPONIBLE - Peut être confirmé")
        print("   Logique: L'inscription sera confirmée immédiatement")
    
    print()
    print("📝 Test de la logique:")
    print("   1. Si VIP épuisé → Liste d'attente")
    print("   2. Si VIP disponible → Confirmation immédiate")
    print("   3. Le prix payé sera celui du billet VIP, pas du billet par défaut")

if __name__ == '__main__':
    test_vip_purchase()














