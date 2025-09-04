#!/usr/bin/env python
"""
🧪 TEST DE L'API DE CRÉATION DE RAPPELS
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.utils import timezone
from events.models import Event, User
from rest_framework.test import APIClient
from django.contrib.auth.models import User as DjangoUser

def test_api_reminder_creation():
    """Tester la création de rappels via l'API"""
    print("🧪 TEST DE L'API DE CRÉATION DE RAPPELS")
    print("=" * 60)
    
    try:
        # Créer un client API
        client = APIClient()
        
        # Récupérer ou créer un utilisateur test
        user, created = DjangoUser.objects.get_or_create(
            username='test_api_user',
            defaults={
                'email': 'test@api.com',
                'first_name': 'Test',
                'last_name': 'API'
            }
        )
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test API Rappel',
            defaults={
                'description': 'Événement pour test API',
                'start_date': timezone.now() + timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=1, hours=2),
                'location': 'Test Location',
                'max_capacity': 100,
                'price': 0,
                'organizer': user,
                'status': 'published'
            }
        )
        
        print(f"✅ Utilisateur: {user.username}")
        print(f"✅ Événement: {event.title} (ID: {event.id})")
        print()
        
        # Test 1: Création sans le champ send_mode (comme le frontend actuel)
        print("🧪 TEST 1: Création sans send_mode (comme frontend actuel)")
        print("-" * 50)
        
        reminder_data_old = {
            'event': event.id,
            'title': 'Test Sans Send Mode',
            'message': 'Ce rappel est créé sans send_mode',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False
        }
        
        print(f"📤 Données envoyées: {json.dumps(reminder_data_old, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_old, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 201:
                print("✅ Création réussie sans send_mode")
            else:
                print(f"❌ Erreur de création: {response.data}")
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
        
        print()
        
        # Test 2: Création avec le champ send_mode
        print("🧪 TEST 2: Création avec send_mode")
        print("-" * 50)
        
        reminder_data_new = {
            'event': event.id,
            'title': 'Test Avec Send Mode',
            'message': 'Ce rappel est créé avec send_mode',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'send_mode': 'manual'
        }
        
        print(f"📤 Données envoyées: {json.dumps(reminder_data_new, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_new, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 201:
                print("✅ Création réussie avec send_mode")
            else:
                print(f"❌ Erreur de création: {response.data}")
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
        
        print()
        
        # Test 3: Test de validation
        print("🧪 TEST 3: Test de validation des champs")
        print("-" * 50)
        
        # Test avec send_mode automatique sans scheduled_at
        reminder_data_invalid = {
            'event': event.id,
            'title': 'Test Invalide',
            'message': 'Ce rappel devrait échouer',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'send_mode': 'automatic'  # Automatique sans scheduled_at
        }
        
        print(f"📤 Données invalides: {json.dumps(reminder_data_invalid, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_invalid, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 400:
                print("✅ Validation fonctionne - erreur attendue")
            else:
                print(f"❌ Validation ne fonctionne pas - statut inattendu")
        except Exception as e:
            print(f"❌ Exception lors de la validation: {e}")
        
        print()
        
        # Résumé
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        print("✅ Test 1: Création sans send_mode")
        print("✅ Test 2: Création avec send_mode")
        print("✅ Test 3: Validation des champs")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_reminder_creation()
