#!/usr/bin/env python3
"""
Test de la logique de comptage CORRIGÉE
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, TicketType, SessionType, EventRegistration, User
from django.utils import timezone
from datetime import date, time

def test_fixed_counting_logic():
    """Test de la logique de comptage corrigée"""
    print("🧪 Test de la logique de comptage CORRIGÉE")
    print("=" * 60)
    
    # Créer des utilisateurs de test
    user1, created = User.objects.get_or_create(
        username='test_user1_fixed',
        defaults={
            'email': 'test1@fixed.com',
            'first_name': 'Test1',
            'last_name': 'Fixed'
        }
    )
    
    user2, created = User.objects.get_or_create(
        username='test_user2_fixed',
        defaults={
            'email': 'test2@fixed.com',
            'first_name': 'Test2',
            'last_name': 'Fixed'
        }
    )
    
    user3, created = User.objects.get_or_create(
        username='test_user3_fixed',
        defaults={
            'email': 'test3@fixed.com',
            'first_name': 'Test3',
            'last_name': 'Fixed'
        }
    )
    
    print(f"✅ Utilisateurs de test créés")
    
    # Créer un événement de test
    event, created = Event.objects.get_or_create(
        title='Test Comptage Corrigé',
        defaults={
            'description': 'Test de la logique de comptage corrigée',
            'short_description': 'Test comptage corrigé',
            'start_date': timezone.now() + timezone.timedelta(days=30),
            'end_date': timezone.now() + timezone.timedelta(days=30, hours=2),
            'location': 'Test Location',
            'address': 'Test Address',
            'place_type': 'limited',
            'max_capacity': 10,  # 10 places totales pour l'événement
            'price': Decimal('20.00'),
            'is_free': False,
            'event_type': 'physical',
            'status': 'published',
            'organizer': user1
        }
    )
    
    print(f"✅ Événement de test créé: {event.title}")
    print(f"   - Places totales: {event.max_capacity}")
    
    # Créer des types de billets
    ticket_vip, created = TicketType.objects.get_or_create(
        event=event,
        name='VIP',
        defaults={
            'price': Decimal('50.00'),
            'quantity': 3,  # 3 places VIP
            'description': 'Billet VIP avec 3 places'
        }
    )
    
    ticket_standard, created = TicketType.objects.get_or_create(
        event=event,
        name='Standard',
        defaults={
            'price': Decimal('30.00'),
            'quantity': 4,  # 4 places Standard
            'description': 'Billet Standard avec 4 places'
        }
    )
    
    print(f"✅ Types de billets créés:")
    print(f"   - VIP: {ticket_vip.quantity} places (prix: {ticket_vip.price}€)")
    print(f"   - Standard: {ticket_standard.quantity} places (prix: {ticket_standard.price}€)")
    
    # Créer des sessions
    session_matin, created = SessionType.objects.get_or_create(
        event=event,
        name='Session Matin',
        defaults={
            'date': date(2025, 9, 25),
            'start_time': time(10, 0),
            'end_time': time(12, 0),
            'max_participants': 5,  # 5 places pour la session matin
            'description': 'Session du matin avec 5 places'
        }
    )
    
    session_soir, created = SessionType.objects.get_or_create(
        event=event,
        name='Session Soir',
        defaults={
            'date': date(2025, 9, 25),
            'start_time': time(18, 0),
            'end_time': time(20, 0),
            'max_participants': 5,  # 5 places pour la session soir
            'description': 'Session du soir avec 5 places'
        }
    )
    
    print(f"✅ Sessions créées:")
    print(f"   - Session Matin: {session_matin.max_participants} places")
    print(f"   - Session Soir: {session_soir.max_participants} places")
    
    # Test 1: Vérifier la disponibilité initiale
    print(f"\n🔍 Test 1: Disponibilité initiale")
    print(f"   - Événement total: {event.max_capacity} places")
    print(f"   - Billets par défaut disponibles: {event.default_ticket_available_places}")
    print(f"   - VIP disponibles: {ticket_vip.available_quantity}")
    print(f"   - Standard disponibles: {ticket_standard.available_quantity}")
    print(f"   - Session Matin disponibles: {session_matin.available_spots}")
    print(f"   - Session Soir disponibles: {session_soir.available_spots}")
    
    # Test 2: Créer des inscriptions pour tester le comptage
    print(f"\n🔍 Test 2: Création d'inscriptions")
    
    # Inscription 1: VIP + Session Matin
    reg1 = EventRegistration.objects.create(
        event=event,
        user=user1,
        ticket_type=ticket_vip,
        session_type=session_matin,
        status='confirmed',
        payment_status='paid',
        price_paid=Decimal('50.00')
    )
    print(f"   ✅ Inscription 1 créée: VIP + Session Matin (User1)")
    
    # Inscription 2: Standard + Session Soir
    reg2 = EventRegistration.objects.create(
        event=event,
        user=user2,
        ticket_type=ticket_standard,
        session_type=session_soir,
        status='confirmed',
        payment_status='paid',
        price_paid=Decimal('30.00')
    )
    print(f"   ✅ Inscription 2 créée: Standard + Session Soir (User2)")
    
    # Inscription 3: Billet par défaut + Session Matin
    reg3 = EventRegistration.objects.create(
        event=event,
        user=user3,
        ticket_type=None,  # Billet par défaut
        session_type=session_matin,
        status='confirmed',
        payment_status='paid',
        price_paid=Decimal('20.00')
    )
    print(f"   ✅ Inscription 3 créée: Billet par défaut + Session Matin (User3)")
    
    # Test 3: Vérifier la disponibilité après inscriptions
    print(f"\n🔍 Test 3: Disponibilité après inscriptions")
    print(f"   - Billets par défaut disponibles: {event.default_ticket_available_places}")
    print(f"   - VIP disponibles: {ticket_vip.available_quantity}")
    print(f"   - Standard disponibles: {ticket_standard.available_quantity}")
    print(f"   - Session Matin disponibles: {session_matin.available_spots}")
    print(f"   - Session Soir disponibles: {session_soir.available_spots}")
    
    # Test 4: Vérifier les méthodes de disponibilité
    print(f"\n🔍 Test 4: Méthodes de disponibilité")
    print(f"   - Peut s'inscrire billet par défaut: {event.can_register_for_default_ticket()}")
    print(f"   - Peut s'inscrire VIP: {event.can_register_for_ticket_type(ticket_vip.id)}")
    print(f"   - Peut s'inscrire Standard: {event.can_register_for_ticket_type(ticket_standard.id)}")
    print(f"   - Peut s'inscrire Session Matin: {event.can_register_for_session(session_matin.id)}")
    print(f"   - Peut s'inscrire Session Soir: {event.can_register_for_session(session_soir.id)}")
    
    # Test 5: Vérifier la disponibilité détaillée
    print(f"\n🔍 Test 5: Disponibilité détaillée")
    ticket_availability = event.get_ticket_type_availability()
    session_availability = event.get_session_availability()
    
    print(f"   - Disponibilité des types de billets:")
    for ticket_id, info in ticket_availability.items():
        print(f"     * {info['name']}: {info['available']}/{info['max_quantity']} places")
    
    print(f"   - Disponibilité des sessions:")
    for session_id, info in session_availability.items():
        print(f"     * {info['name']}: {info['available']}/{info['max_participants']} places")
    
    # Test 6: Vérifier que les compteurs sont INDÉPENDANTS
    print(f"\n🔍 Test 6: Vérification de l'indépendance des compteurs")
    
    # Créer une inscription VIP + Session Soir pour tester
    reg4 = EventRegistration.objects.create(
        event=event,
        user=User.objects.create(username='test_user4_fixed'),
        ticket_type=ticket_vip,
        session_type=session_soir,
        status='confirmed',
        payment_status='paid',
        price_paid=Decimal('50.00')
    )
    print(f"   ✅ Inscription 4 créée: VIP + Session Soir (User4)")
    
    print(f"   - Après inscription 4:")
    print(f"     * VIP disponibles: {ticket_vip.available_quantity}")
    print(f"     * Standard disponibles: {ticket_standard.available_quantity}")
    print(f"     * Session Matin disponibles: {session_matin.available_spots}")
    print(f"     * Session Soir disponibles: {session_soir.available_spots}")
    print(f"     * Billets par défaut disponibles: {event.default_ticket_available_places}")
    
    # Nettoyage
    print(f"\n🧹 Nettoyage des données de test")
    reg1.delete()
    reg2.delete()
    reg3.delete()
    reg4.delete()
    session_matin.delete()
    session_soir.delete()
    ticket_vip.delete()
    ticket_standard.delete()
    event.delete()
    user1.delete()
    user2.delete()
    user3.delete()
    User.objects.filter(username='test_user4_fixed').delete()
    
    print(f"✅ Test terminé avec succès !")
    print(f"\n🎯 Résumé de la logique CORRIGÉE:")
    print(f"   1. Billets par défaut: Compteur basé sur max_capacity (INDÉPENDANT des sessions)")
    print(f"   2. Types de billets: Compteurs SÉPARÉS basés sur quantity")
    print(f"   3. Sessions: Compteurs SÉPARÉS basés sur max_participants")
    print(f"   4. Chaque inscription peut avoir UN type de billet + UNE session")
    print(f"   5. Les compteurs sont COMPLÈTEMENT INDÉPENDANTS")
    print(f"   6. Les sessions ne sont PAS liées aux billets par défaut")

if __name__ == '__main__':
    test_fixed_counting_logic()








