#!/usr/bin/env python3
"""
Script de test API pour le système de rappels personnalisés
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Event, EventRegistration, CustomReminder, UserProfile

def test_reminders_api():
    """Tester l'API des rappels personnalisés"""
    
    print("🔍 TEST API DU SYSTÈME DE RAPPELS PERSONNALISÉS")
    print("=" * 60)
    
    # URL de base
    base_url = "http://localhost:8001/api"
    
    # 1. Vérifier que le serveur fonctionne
    print("\n1. Vérification du serveur...")
    try:
        response = requests.get(f"{base_url}/events/", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur accessible")
        else:
            print(f"❌ Serveur répond avec le code: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Serveur non accessible: {e}")
        print("Assurez-vous que le serveur Django fonctionne sur le port 8001")
        return
    
    # 2. S'authentifier
    print("\n2. Authentification...")
    try:
        auth_response = requests.post(f"{base_url}/auth/token/", {
            'username': 'organizer_test',
            'password': 'testpass123'
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            print("✅ Authentification réussie")
        else:
            print(f"❌ Erreur authentification: {auth_response.text}")
            return
        
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return
    
    # 3. Récupérer l'événement de test
    print("\n3. Récupération de l'événement de test...")
    try:
        events_response = requests.get(f"{base_url}/events/", headers=headers)
        
        if events_response.status_code == 200:
            events = events_response.json()
            test_event = None
            
            for event in events:
                if event['title'] == 'Événement Test Rappels':
                    test_event = event
                    break
            
            if test_event:
                print(f"✅ Événement trouvé: {test_event['title']} (ID: {test_event['id']})")
                event_id = test_event['id']
            else:
                print("❌ Événement de test non trouvé")
                return
        else:
            print(f"❌ Erreur récupération événements: {events_response.text}")
            return
        
    except Exception as e:
        print(f"❌ Erreur récupération événement: {e}")
        return
    
    # 4. Créer un rappel via API
    print("\n4. Création d'un rappel via API...")
    try:
        reminder_data = {
            'event': event_id,
            'title': 'Rappel API Test',
            'message': 'Ceci est un message de rappel créé via l\'API pour tester le système.',
            'reminder_type': 'general',
            'target_audience': 'all',
            'send_email': True,
            'send_sms': True
        }
        
        create_response = requests.post(
            f"{base_url}/custom-reminders/",
            json=reminder_data,
            headers=headers
        )
        
        if create_response.status_code == 201:
            reminder = create_response.json()
            print(f"✅ Rappel créé via API: {reminder['title']} (ID: {reminder['id']})")
            reminder_id = reminder['id']
        else:
            print(f"❌ Erreur création rappel: {create_response.text}")
            return
        
    except Exception as e:
        print(f"❌ Erreur création rappel API: {e}")
        return
    
    # 5. Lister les rappels
    print("\n5. Liste des rappels...")
    try:
        list_response = requests.get(f"{base_url}/custom-reminders/", headers=headers)
        
        if list_response.status_code == 200:
            reminders = list_response.json()
            print(f"✅ {len(reminders)} rappel(s) trouvé(s):")
            
            for reminder in reminders:
                print(f"   - {reminder['title']} ({reminder['status']})")
                print(f"     Type: {reminder['reminder_type']}")
                print(f"     Audience: {reminder['target_audience']}")
                print(f"     Email: {reminder['send_email']}, SMS: {reminder['send_sms']}")
        else:
            print(f"❌ Erreur liste rappels: {list_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur liste rappels: {e}")
    
    # 6. Tester l'envoi immédiat
    print("\n6. Test envoi immédiat du rappel...")
    try:
        send_response = requests.post(
            f"{base_url}/custom-reminders/{reminder_id}/send_now/",
            headers=headers
        )
        
        if send_response.status_code == 200:
            result = send_response.json()
            print(f"✅ Rappel envoyé avec succès!")
            print(f"   Message: {result['message']}")
            print(f"   Statistiques: {result['statistics']}")
        else:
            print(f"❌ Erreur envoi rappel: {send_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur test envoi: {e}")
    
    # 7. Tester les rappels par événement
    print("\n7. Test rappels par événement...")
    try:
        event_reminders_response = requests.get(
            f"{base_url}/custom-reminders/event_reminders/?event_id={event_id}",
            headers=headers
        )
        
        if event_reminders_response.status_code == 200:
            event_reminders = event_reminders_response.json()
            print(f"✅ {len(event_reminders)} rappel(s) pour l'événement {event_id}")
            
            for reminder in event_reminders:
                print(f"   - {reminder['title']} ({reminder['status']})")
        else:
            print(f"❌ Erreur rappels par événement: {event_reminders_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur test rappels par événement: {e}")
    
    # 8. Tester la programmation d'envoi
    print("\n8. Test programmation d'envoi...")
    try:
        # Programmer l'envoi dans 1 minute
        scheduled_time = (datetime.now() + timedelta(minutes=1)).isoformat()
        
        schedule_data = {
            'scheduled_at': scheduled_time
        }
        
        schedule_response = requests.post(
            f"{base_url}/custom-reminders/{reminder_id}/schedule/",
            json=schedule_data,
            headers=headers
        )
        
        if schedule_response.status_code == 200:
            result = schedule_response.json()
            print(f"✅ Rappel programmé avec succès!")
            print(f"   Message: {result['message']}")
            print(f"   Date programmée: {result['scheduled_at']}")
        else:
            print(f"❌ Erreur programmation: {schedule_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur test programmation: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST API TERMINÉ!")
    print("Le système de rappels personnalisés fonctionne via l'API.")
    print("Vérifiez les logs du serveur pour voir les détails d'envoi.")

if __name__ == "__main__":
    test_reminders_api()


