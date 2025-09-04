#!/usr/bin/env python
"""
🧪 TEST DE L'API AVEC AUTHENTIFICATION
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
from rest_framework_simplejwt.tokens import RefreshToken

def test_api_with_auth():
    """Tester l'API avec authentification"""
    print("🧪 TEST DE L'API AVEC AUTHENTIFICATION")
    print("=" * 60)
    
    try:
        # Créer un client API
        client = APIClient()
        
        # Récupérer ou créer un utilisateur test
        user, created = DjangoUser.objects.get_or_create(
            username='test_api_auth',
            defaults={
                'email': 'test@apiauth.com',
                'first_name': 'Test',
                'last_name': 'APIAuth'
            }
        )
        
        # Générer un token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Configurer l'authentification
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test API Auth',
            defaults={
                'description': 'Événement pour test API avec auth',
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
        print(f"✅ Token: {access_token[:20]}...")
        print(f"✅ Événement: {event.title} (ID: {event.id})")
        print()
        
        # Test 1: Création sans send_mode (comme le frontend actuel)
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
                reminder_id_old = response.data['id']
            else:
                print(f"❌ Erreur de création: {response.data}")
                reminder_id_old = None
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
            reminder_id_old = None
        
        print()
        
        # Test 2: Création avec send_mode manuel
        print("🧪 TEST 2: Création avec send_mode manuel")
        print("-" * 50)
        
        reminder_data_manual = {
            'event': event.id,
            'title': 'Test Mode Manuel',
            'message': 'Ce rappel est créé en mode manuel',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'send_mode': 'manual'
        }
        
        print(f"📤 Données envoyées: {json.dumps(reminder_data_manual, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_manual, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 201:
                print("✅ Création réussie avec send_mode manuel")
                reminder_id_manual = response.data['id']
                print(f"📊 Statut du rappel: {response.data['status']}")
            else:
                print(f"❌ Erreur de création: {response.data}")
                reminder_id_manual = None
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
            reminder_id_manual = None
        
        print()
        
        # Test 3: Création avec send_mode automatique
        print("🧪 TEST 3: Création avec send_mode automatique")
        print("-" * 50)
        
        future_time = timezone.now() + timedelta(minutes=5)
        reminder_data_auto = {
            'event': event.id,
            'title': 'Test Mode Automatique',
            'message': 'Ce rappel est créé en mode automatique',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'scheduled_at': future_time.isoformat(),
            'send_mode': 'automatic'
        }
        
        print(f"📤 Données envoyées: {json.dumps(reminder_data_auto, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_auto, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 201:
                print("✅ Création réussie avec send_mode automatique")
                reminder_id_auto = response.data['id']
                print(f"📊 Statut du rappel: {response.data['status']}")
            else:
                print(f"❌ Erreur de création: {response.data}")
                reminder_id_auto = None
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
            reminder_id_auto = None
        
        print()
        
        # Test 4: Test de l'envoi manuel
        print("🧪 TEST 4: Test de l'envoi manuel")
        print("-" * 50)
        
        if reminder_id_manual:
            try:
                response = client.post(f'/api/custom-reminders/{reminder_id_manual}/send_now/', format='json')
                print(f"📊 Statut de réponse: {response.status_code}")
                print(f"📊 Données de réponse: {response.data}")
                
                if response.status_code == 200:
                    print("✅ Envoi manuel réussi")
                else:
                    print(f"❌ Erreur envoi manuel: {response.data}")
            except Exception as e:
                print(f"❌ Exception lors de l'envoi: {e}")
        
        print()
        
        # Résumé
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        print(f"✅ Test 1 (sans send_mode): {'Réussi' if reminder_id_old else 'Échec'}")
        print(f"✅ Test 2 (mode manuel): {'Réussi' if reminder_id_manual else 'Échec'}")
        print(f"✅ Test 3 (mode automatique): {'Réussi' if reminder_id_auto else 'Échec'}")
        print(f"✅ Test 4 (envoi manuel): {'Réussi' if reminder_id_manual else 'Échec'}")
        
        # Nettoyage
        print("\n🧹 Nettoyage des tests...")
        if reminder_id_old:
            from events.models import CustomReminder
            CustomReminder.objects.filter(id=reminder_id_old).delete()
        if reminder_id_manual:
            CustomReminder.objects.filter(id=reminder_id_manual).delete()
        if reminder_id_auto:
            CustomReminder.objects.filter(id=reminder_id_auto).delete()
        print("✅ Tests nettoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_with_auth()
