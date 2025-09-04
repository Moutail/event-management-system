#!/usr/bin/env python
"""
🧪 TEST DE L'API DES ÉVÉNEMENTS POUR LES RAPPELS
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.utils import timezone
from events.models import Event, User
from events.views import EventViewSet
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser

def test_events_api():
    """Tester l'API des événements pour les rappels"""
    print("🧪 TEST DE L'API DES ÉVÉNEMENTS POUR LES RAPPELS")
    print("=" * 60)
    
    try:
        # Récupérer ou créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='test_events_api',
            defaults={
                'email': 'test@eventsapi.com',
                'first_name': 'Test',
                'last_name': 'EventsAPI'
            }
        )
        
        # Créer quelques événements de test
        event1, created = Event.objects.get_or_create(
            title='Test Event 1 pour Rappels',
            defaults={
                'description': 'Événement test 1 pour les rappels',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location 1',
                'max_capacity': 100,
                'price': 0,
                'organizer': user,
                'status': 'published'
            }
        )
        
        event2, created = Event.objects.get_or_create(
            title='Test Event 2 pour Rappels',
            defaults={
                'description': 'Événement test 2 pour les rappels',
                'start_date': timezone.now() + timedelta(days=2),
                'end_date': timezone.now() + timedelta(days=2, hours=3),
                'location': 'Test Location 2',
                'max_capacity': 50,
                'price': 10,
                'organizer': user,
                'status': 'published'
            }
        )
        
        print(f"✅ Utilisateur: {user.username}")
        print(f"✅ Événements créés: {Event.objects.filter(organizer=user).count()}")
        print()
        
        # Test 1: Lister les événements via l'API
        print("🧪 TEST 1: Lister les événements via l'API")
        print("-" * 50)
        
        factory = APIRequestFactory()
        request = factory.get('/api/events/')
        request.user = user
        
        # Créer l'instance de la vue
        viewset = EventViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        viewset.action = 'list'
        
        try:
            response = viewset.list(request)
            print(f"✅ Réponse de l'API: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"✅ Nombre d'événements retournés: {len(response.data)}")
                for event in response.data:
                    print(f"   - ID: {event.get('id')}, Titre: {event.get('title')}, Statut: {event.get('status')}")
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à l'API: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Test 2: Vérifier les événements disponibles pour les rappels
        print("🧪 TEST 2: Événements disponibles pour les rappels")
        print("-" * 50)
        
        # Événements publiés
        published_events = Event.objects.filter(status='published')
        print(f"📋 Événements publiés: {published_events.count()}")
        for event in published_events:
            print(f"   - ID: {event.id}, Titre: {event.title}, Organisateur: {event.organizer.username}")
        
        # Événements de l'utilisateur
        user_events = Event.objects.filter(organizer=user)
        print(f"📋 Événements de l'utilisateur: {user_events.count()}")
        for event in user_events:
            print(f"   - ID: {event.id}, Titre: {event.title}, Statut: {event.status}")
        
        print()
        
        # Test 3: Vérifier la structure des données pour le frontend
        print("🧪 TEST 3: Structure des données pour le frontend")
        print("-" * 50)
        
        # Simuler ce que le frontend devrait recevoir
        events_for_reminders = Event.objects.filter(
            Q(status='published') | Q(organizer=user)
        ).distinct()
        
        print(f"📋 Événements disponibles pour les rappels: {events_for_reminders.count()}")
        
        events_data = []
        for event in events_for_reminders:
            event_data = {
                'id': event.id,
                'title': event.title,
                'start_date': event.start_date,
                'end_date': event.end_date,
                'location': event.location,
                'status': event.status,
                'organizer': event.organizer.username
            }
            events_data.append(event_data)
            print(f"   - {event_data}")
        
        print()
        
        # Test 4: Vérifier les permissions
        print("🧪 TEST 4: Vérification des permissions")
        print("-" * 50)
        
        # Test avec utilisateur non authentifié
        anonymous_request = factory.get('/api/events/')
        anonymous_request.user = AnonymousUser()
        
        viewset_anon = EventViewSet()
        viewset_anon.request = anonymous_request
        viewset_anon.format_kwarg = None
        viewset_anon.action = 'list'
        
        try:
            response_anon = viewset_anon.list(anonymous_request)
            print(f"✅ Réponse pour utilisateur anonyme: {response_anon.status_code}")
            if hasattr(response_anon, 'data'):
                print(f"✅ Événements visibles pour anonyme: {len(response_anon.data)}")
        except Exception as e:
            print(f"❌ Erreur pour utilisateur anonyme: {e}")
        
        print()
        
        # Résumé
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        print(f"✅ Événements créés: {Event.objects.filter(organizer=user).count()}")
        print(f"✅ Événements publiés: {published_events.count()}")
        print(f"✅ Événements disponibles pour rappels: {events_for_reminders.count()}")
        
        # Nettoyage
        print("\n🧹 Nettoyage des tests...")
        event1.delete()
        event2.delete()
        print("✅ Tests nettoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_events_api()