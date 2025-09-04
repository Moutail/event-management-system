#!/usr/bin/env python3
"""
Script de test pour le système de rappels personnalisés
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
from events.models import Event, EventRegistration, CustomReminder

def test_custom_reminders():
    """Tester le système de rappels personnalisés"""
    
    print("🔍 TEST DU SYSTÈME DE RAPPELS PERSONNALISÉS")
    print("=" * 50)
    
    # URL de base
    base_url = "http://localhost:8001/api"
    
    # 1. Créer un utilisateur organisateur
    print("\n1. Création d'un organisateur...")
    try:
        organizer = User.objects.create_user(
            username='organizer_test',
            email='organizer@test.com',
            password='testpass123',
            first_name='Organisateur',
            last_name='Test'
        )
        from events.models import UserProfile
        UserProfile.objects.create(
            user=organizer,
            role='organizer',
            status_approval='approved'
        )
        print(f"✅ Organisateur créé: {organizer.username}")
    except Exception as e:
        print(f"❌ Erreur création organisateur: {e}")
        return
    
    # 2. Créer un événement
    print("\n2. Création d'un événement...")
    try:
        event = Event.objects.create(
            title="Événement Test Rappels",
            description="Événement pour tester les rappels personnalisés",
            start_date=datetime.now() + timedelta(days=7),
            end_date=datetime.now() + timedelta(days=7, hours=3),
            location="Lieu Test",
            organizer=organizer,
            status='published',
            price=0,
            is_free=True
        )
        print(f"✅ Événement créé: {event.title} (ID: {event.id})")
    except Exception as e:
        print(f"❌ Erreur création événement: {e}")
        return
    
    # 3. Créer des inscriptions
    print("\n3. Création d'inscriptions...")
    try:
        # Inscription utilisateur
        user = User.objects.create_user(
            username='participant1',
            email='participant1@test.com',
            password='testpass123'
        )
        from events.models import UserProfile
        UserProfile.objects.create(
            user=user,
            role='participant',
            status_approval='approved',
            phone='5141234567',
            country='CA'
        )
        
        registration1 = EventRegistration.objects.create(
            event=event,
            user=user,
            status='confirmed'
        )
        print(f"✅ Inscription utilisateur créée: {user.username}")
        
        # Inscription invité
        registration2 = EventRegistration.objects.create(
            event=event,
            guest_full_name='Invité Test',
            guest_email='invite@test.com',
            guest_phone='4387654321',
            guest_country='CA',
            is_guest_registration=True,
            status='confirmed'
        )
        print(f"✅ Inscription invité créée: {registration2.guest_full_name}")
        
    except Exception as e:
        print(f"❌ Erreur création inscriptions: {e}")
        return
    
    # 4. Tester l'API de création de rappel
    print("\n4. Test création de rappel via API...")
    try:
        # Authentification
        auth_response = requests.post(f"{base_url}/auth/token/", {
            'username': 'organizer_test',
            'password': 'testpass123'
        })
        
        if auth_response.status_code != 200:
            print(f"❌ Erreur authentification: {auth_response.text}")
            return
        
        token = auth_response.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Créer un rappel
        reminder_data = {
            'event': event.id,
            'title': 'Rappel Test',
            'message': 'Ceci est un message de rappel personnalisé pour tester le système.',
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
            print(f"✅ Rappel créé: {reminder['title']} (ID: {reminder['id']})")
            reminder_id = reminder['id']
        else:
            print(f"❌ Erreur création rappel: {create_response.text}")
            return
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return
    
    # 5. Tester l'envoi immédiat
    print("\n5. Test envoi immédiat du rappel...")
    try:
        send_response = requests.post(
            f"{base_url}/custom-reminders/{reminder_id}/send_now/",
            headers=headers
        )
        
        if send_response.status_code == 200:
            result = send_response.json()
            print(f"✅ Rappel envoyé avec succès!")
            print(f"   Statistiques: {result['statistics']}")
        else:
            print(f"❌ Erreur envoi rappel: {send_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur test envoi: {e}")
    
    # 6. Tester la récupération des rappels
    print("\n6. Test récupération des rappels...")
    try:
        list_response = requests.get(
            f"{base_url}/custom-reminders/",
            headers=headers
        )
        
        if list_response.status_code == 200:
            reminders = list_response.json()
            print(f"✅ {len(reminders)} rappel(s) récupéré(s)")
            for reminder in reminders:
                print(f"   - {reminder['title']} ({reminder['status']})")
        else:
            print(f"❌ Erreur récupération rappels: {list_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur test récupération: {e}")
    
    # 7. Tester les rappels par événement
    print("\n7. Test rappels par événement...")
    try:
        event_reminders_response = requests.get(
            f"{base_url}/custom-reminders/event_reminders/?event_id={event.id}",
            headers=headers
        )
        
        if event_reminders_response.status_code == 200:
            event_reminders = event_reminders_response.json()
            print(f"✅ {len(event_reminders)} rappel(s) pour l'événement {event.id}")
        else:
            print(f"❌ Erreur rappels par événement: {event_reminders_response.text}")
        
    except Exception as e:
        print(f"❌ Erreur test rappels par événement: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TEST TERMINÉ!")
    print("Vérifiez les logs du serveur pour voir les détails d'envoi des emails et SMS.")

if __name__ == "__main__":
    test_custom_reminders()


