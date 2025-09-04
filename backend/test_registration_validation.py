#!/usr/bin/env python
"""
Test de la validation des inscriptions pour vérifier la logique des billets
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, User, UserProfile, TicketType, EventRegistration
from events.serializers import EventRegistrationCreateSerializer
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.db import transaction

def test_registration_validation():
    """Test de la validation des inscriptions"""
    print("🧪 Test de la validation des inscriptions")
    print("=" * 60)
    
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
    
    # Simuler une demande d'inscription
    print("🔍 Test de validation d'inscription:")
    
    # Créer un utilisateur de test
    test_user, created = User.objects.get_or_create(
        username='test_validation_user',
        defaults={'email': 'test@test.com'}
    )
    
    if created:
        print(f"   ✅ Utilisateur de test créé: {test_user.username}")
    else:
        print(f"   ✅ Utilisateur de test existant: {test_user.username}")
    
    # Créer une requête simulée
    factory = RequestFactory()
    request = factory.post('/fake-url/')
    request.user = test_user
    
    # Données d'inscription
    registration_data = {
        'event': event,
        'ticket_type': vip_ticket,
        'notes': 'Test de validation',
        'special_requirements': ''
    }
    
    print(f"   📝 Données d'inscription:")
    print(f"      Événement: {event.title}")
    print(f"      Type de billet: {vip_ticket.name}")
    print(f"      Prix: ${vip_ticket.price}")
    print()
    
    # Tester la validation
    try:
        serializer = EventRegistrationCreateSerializer(
            data=registration_data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            print("   ✅ Validation OK - Inscription possible")
            
            # Tester la création
            try:
                registration = serializer.save()
                print(f"   ✅ Inscription créée - ID: {registration.id}")
                print(f"   ✅ Statut: {registration.status}")
                print(f"   ✅ Paiement: {registration.payment_status}")
                
                # Nettoyer l'inscription de test
                registration.delete()
                print("   🧹 Inscription de test supprimée")
                
            except Exception as e:
                print(f"   ❌ Erreur lors de la création: {str(e)}")
        else:
            print("   ❌ Validation échouée:")
            for field, errors in serializer.errors.items():
                print(f"      {field}: {errors}")
                
    except Exception as e:
        print(f"   ❌ Erreur lors de la validation: {str(e)}")
    
    print()
    print("✅ Test terminé!")

if __name__ == '__main__':
    test_registration_validation()













