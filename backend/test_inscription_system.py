#!/usr/bin/env python
"""
Test du système d'inscription avec approbation
"""
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def test_inscription_system():
    """Tester le système d'inscription complet"""
    print("🧪 Test du système d'inscription avec approbation...")
    
    BASE_URL = 'http://localhost:8001/api'
    
    # 1. Test d'inscription d'un participant (accès immédiat)
    print("\n1️⃣ Test inscription participant...")
    participant_data = {
        'username': 'test_participant',
        'email': 'participant@test.com',
        'password': 'testpass123',
        'first_name': 'Jean',
        'last_name': 'Dupont',
        'phone': '0123456789',
        'role': 'participant'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=participant_data)
        if response.status_code == 201:
            print("   ✅ Participant créé avec succès")
            participant_response = response.json()
            print(f"   📧 Message: {participant_response['message']}")
            print(f"   🔐 Statut: {participant_response['user']['status_approval']}")
        else:
            print(f"   ❌ Erreur participant: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
    
    # 2. Test d'inscription d'un organisateur (en attente d'approbation)
    print("\n2️⃣ Test inscription organisateur...")
    organizer_data = {
        'username': 'test_organizer',
        'email': 'organizer@test.com',
        'password': 'testpass123',
        'first_name': 'Marie',
        'last_name': 'Martin',
        'phone': '0987654321',
        'role': 'organizer'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=organizer_data)
        if response.status_code == 201:
            print("   ✅ Organisateur créé avec succès")
            organizer_response = response.json()
            print(f"   📧 Message: {organizer_response['message']}")
            print(f"   🔐 Statut: {organizer_response['user']['status_approval']}")
        else:
            print(f"   ❌ Erreur organisateur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
    
    # 3. Vérifier les profils en base
    print("\n3️⃣ Vérification des profils en base...")
    try:
        participant_user = User.objects.get(username='test_participant')
        participant_profile = UserProfile.objects.get(user=participant_user)
        print(f"   👤 Participant: {participant_profile.user.username} - Rôle: {participant_profile.role} - Statut: {participant_profile.status_approval}")
        
        organizer_user = User.objects.get(username='test_organizer')
        organizer_profile = UserProfile.objects.get(user=organizer_user)
        print(f"   🎪 Organisateur: {organizer_profile.user.username} - Rôle: {organizer_profile.role} - Statut: {organizer_profile.status_approval}")
        
    except Exception as e:
        print(f"   ❌ Erreur vérification base: {e}")
    
    # 4. Test de la liste des approbations en attente
    print("\n4️⃣ Test liste des approbations...")
    try:
        # D'abord se connecter en tant que super admin
        login_data = {
            'username': 'window7',  # Remplacer par un vrai super admin
            'password': 'password123'
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Récupérer la liste des approbations
            approvals_response = requests.get(f"{BASE_URL}/admin/pending_organizer_approvals/", headers=headers)
            if approvals_response.status_code == 200:
                approvals = approvals_response.json()
                print(f"   ✅ Approbations récupérées: {approvals['count']} en attente")
                for approval in approvals['pending_approvals']:
                    print(f"   📋 {approval['username']} - {approval['email']} - {approval['status_approval']}")
            else:
                print(f"   ❌ Erreur récupération approbations: {approvals_response.status_code}")
        else:
            print(f"   ❌ Erreur connexion super admin: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur test approbations: {e}")
    
    print("\n✅ Test terminé !")

if __name__ == '__main__':
    test_inscription_system()
















