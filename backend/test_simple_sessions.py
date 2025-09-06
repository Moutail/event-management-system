#!/usr/bin/env python3
"""
Test des sessions SIMPLIFIÉES
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, SessionType, EventRegistration, User
from django.utils import timezone

def test_simple_sessions():
    """Test des sessions simplifiées"""
    print("🧪 Test des sessions SIMPLIFIÉES")
    print("=" * 50)
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_user_simple',
        defaults={
            'email': 'test@simple.com',
            'first_name': 'Test',
            'last_name': 'Simple'
        }
    )
    
    print(f"✅ Utilisateur de test créé")
    
    # Créer un événement de test
    event, created = Event.objects.get_or_create(
        title='Test Sessions Simples',
        defaults={
            'description': 'Test des sessions simplifiées',
            'short_description': 'Test simple',
            'start_date': timezone.now() + timezone.timedelta(days=30),
            'end_date': timezone.now() + timezone.timedelta(days=30, hours=2),
            'location': 'Test Location',
            'address': 'Test Address',
            'place_type': 'limited',
            'max_capacity': 10,
            'price': Decimal('20.00'),
            'is_free': False,
            'event_type': 'physical',
            'status': 'published',
            'organizer': user
        }
    )
    
    print(f"✅ Événement de test créé: {event.title}")
    
    # Créer des sessions simples
    session1, created = SessionType.objects.get_or_create(
        event=event,
        name='Session Matin',
        defaults={
            'is_active': True,
            'is_mandatory': True,
            'display_order': 1
        }
    )
    
    session2, created = SessionType.objects.get_or_create(
        event=event,
        name='Session Soir',
        defaults={
            'is_active': True,
            'is_mandatory': True,
            'display_order': 2
        }
    )
    
    print(f"✅ Sessions créées:")
    print(f"   - {session1.name} (active: {session1.is_active}, obligatoire: {session1.is_mandatory})")
    print(f"   - {session2.name} (active: {session2.is_active}, obligatoire: {session2.is_mandatory})")
    
    # Test 1: Vérifier les propriétés des sessions
    print(f"\n🔍 Test 1: Propriétés des sessions")
    print(f"   - Session 1 disponible: {session1.is_available}")
    print(f"   - Session 2 disponible: {session2.is_available}")
    
    # Test 2: Créer des inscriptions avec sessions
    print(f"\n🔍 Test 2: Création d'inscriptions avec sessions")
    
    reg1 = EventRegistration.objects.create(
        event=event,
        user=user,
        session_type=session1,
        status='confirmed',
        payment_status='paid',
        price_paid=Decimal('20.00')
    )
    print(f"   ✅ Inscription 1 créée: {session1.name}")
    
    # Test 3: Vérifier la disponibilité des sessions
    print(f"\n🔍 Test 3: Disponibilité des sessions")
    session_availability = event.get_session_availability()
    
    for session_id, info in session_availability.items():
        print(f"   - {info['name']}: {info['confirmed_count']} participants confirmés")
        print(f"     * Active: {info['is_active']}")
        print(f"     * Obligatoire: {info['is_mandatory']}")
    
    # Test 4: Vérifier que l'API fonctionne
    print(f"\n🔍 Test 4: Test de l'API des sessions")
    try:
        from events.serializers import SessionTypeSerializer
        serializer = SessionTypeSerializer(session1)
        data = serializer.data
        print(f"   ✅ SessionTypeSerializer fonctionne:")
        print(f"     * ID: {data.get('id')}")
        print(f"     * Nom: {data.get('name')}")
        print(f"     * Disponible: {data.get('is_available_for_registration')}")
    except Exception as e:
        print(f"   ❌ SessionTypeSerializer échoue: {e}")
    
    # Nettoyage
    print(f"\n🧹 Nettoyage des données de test")
    reg1.delete()
    session1.delete()
    session2.delete()
    event.delete()
    user.delete()
    
    print(f"✅ Test terminé avec succès !")
    print(f"\n🎯 Résumé des sessions SIMPLIFIÉES:")
    print(f"   1. Seulement: nom, actif, obligatoire, ordre")
    print(f"   2. PAS de dates, horaires, capacité")
    print(f"   3. Logique simple: si actif = disponible")
    print(f"   4. Pas de comptage complexe")

if __name__ == '__main__':
    test_simple_sessions()











