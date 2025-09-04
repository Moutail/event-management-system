#!/usr/bin/env python
"""
🧪 TEST D'INTÉGRATION FRONTEND - VÉRIFICATION DU CHAMP send_mode
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

def test_frontend_integration():
    """Tester l'intégration frontend avec le champ send_mode"""
    print("🧪 TEST D'INTÉGRATION FRONTEND - CHAMP send_mode")
    print("=" * 60)
    
    try:
        # Créer un client API
        client = APIClient()
        
        # Récupérer ou créer un utilisateur test
        user, created = DjangoUser.objects.get_or_create(
            username='test_frontend_integration',
            defaults={
                'email': 'test@frontend.com',
                'first_name': 'Test',
                'last_name': 'Frontend'
            }
        )
        
        # Générer un token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Configurer l'authentification
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Récupérer ou créer un événement test
        event, created = Event.objects.get_or_create(
            title='Test Frontend Integration',
            defaults={
                'description': 'Événement pour test frontend',
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
        
        # Test 1: Simulation exacte du frontend - Mode manuel
        print("🧪 TEST 1: Simulation frontend - Mode manuel")
        print("-" * 50)
        
        future_time = timezone.now() + timedelta(minutes=2)
        reminder_data_frontend_manual = {
            'event': event.id,
            'title': 'Test Frontend Manuel',
            'message': 'Ce rappel simule le frontend en mode manuel',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'scheduled_at': future_time.isoformat(),
            'send_mode': 'manual'  # Mode manuel avec heure programmée
        }
        
        print(f"📤 Données envoyées: {json.dumps(reminder_data_frontend_manual, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_frontend_manual, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 201:
                print("✅ Création réussie")
                reminder_manual_id = response.data['id']
                print(f"📊 ID du rappel: {reminder_manual_id}")
                print(f"📊 Statut du rappel: {response.data['status']}")
                print(f"📊 Heure programmée: {response.data['scheduled_at']}")
                
                # Vérifier dans la base de données
                from events.models import CustomReminder
                reminder = CustomReminder.objects.get(id=reminder_manual_id)
                print(f"📊 Statut en base: {reminder.status}")
                print(f"📊 Heure en base: {reminder.scheduled_at}")
            else:
                print(f"❌ Erreur de création: {response.data}")
                return
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
            return
        
        print()
        
        # Test 2: Simulation exacte du frontend - Mode automatique
        print("🧪 TEST 2: Simulation frontend - Mode automatique")
        print("-" * 50)
        
        future_time_auto = timezone.now() + timedelta(minutes=3)
        reminder_data_frontend_auto = {
            'event': event.id,
            'title': 'Test Frontend Automatique',
            'message': 'Ce rappel simule le frontend en mode automatique',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': False,
            'scheduled_at': future_time_auto.isoformat(),
            'send_mode': 'automatic'  # Mode automatique
        }
        
        print(f"📤 Données envoyées: {json.dumps(reminder_data_frontend_auto, indent=2)}")
        
        try:
            response = client.post('/api/custom-reminders/', reminder_data_frontend_auto, format='json')
            print(f"📊 Statut de réponse: {response.status_code}")
            print(f"📊 Données de réponse: {response.data}")
            
            if response.status_code == 201:
                print("✅ Création réussie")
                reminder_auto_id = response.data['id']
                print(f"📊 ID du rappel: {reminder_auto_id}")
                print(f"📊 Statut du rappel: {response.data['status']}")
                print(f"📊 Heure programmée: {response.data['scheduled_at']}")
                
                # Vérifier dans la base de données
                reminder = CustomReminder.objects.get(id=reminder_auto_id)
                print(f"📊 Statut en base: {reminder.status}")
                print(f"📊 Heure en base: {reminder.scheduled_at}")
            else:
                print(f"❌ Erreur de création: {response.data}")
                return
        except Exception as e:
            print(f"❌ Exception lors de la création: {e}")
            return
        
        print()
        
        # Test 3: Vérification des logs de debug
        print("🧪 TEST 3: Vérification des logs de debug")
        print("-" * 50)
        print("🔍 Vérifiez les logs ci-dessus pour voir si le champ send_mode est traité correctement")
        print("🔍 Recherchez les messages 'Mode d'envoi choisi' dans les logs")
        
        print()
        
        # Test 4: Traitement automatique
        print("🧪 TEST 4: Test du traitement automatique")
        print("-" * 50)
        
        print("🚀 Lancement du traitement automatique...")
        from run_reminders_manual import process_scheduled_reminders
        result = process_scheduled_reminders()
        print(f"📊 Résultat traitement automatique: {result}")
        
        # Vérifier le statut des rappels après traitement
        if 'reminder_manual_id' in locals():
            reminder = CustomReminder.objects.get(id=reminder_manual_id)
            print(f"📊 Rappel manuel après traitement: {reminder.status}")
        
        if 'reminder_auto_id' in locals():
            reminder = CustomReminder.objects.get(id=reminder_auto_id)
            print(f"📊 Rappel automatique après traitement: {reminder.status}")
        
        print()
        
        # Résumé
        print("📊 RÉSUMÉ DES TESTS:")
        print("-" * 30)
        print(f"✅ Test 1 (mode manuel): {'Réussi' if 'reminder_manual_id' in locals() else 'Échec'}")
        print(f"✅ Test 2 (mode automatique): {'Réussi' if 'reminder_auto_id' in locals() else 'Échec'}")
        print(f"✅ Test 3 (logs debug): Vérifiez les logs ci-dessus")
        print(f"✅ Test 4 (traitement): {result}")
        
        # Nettoyage
        print("\n🧹 Nettoyage des tests...")
        if 'reminder_manual_id' in locals():
            CustomReminder.objects.filter(id=reminder_manual_id).delete()
        if 'reminder_auto_id' in locals():
            CustomReminder.objects.filter(id=reminder_auto_id).delete()
        print("✅ Tests nettoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_integration()
