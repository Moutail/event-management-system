#!/usr/bin/env python
"""
Test de connexion frontend-backend pour le super admin
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken

def test_frontend_connection():
    print("🔍 TEST DE CONNEXION FRONTEND-BACKEND")
    print("=" * 50)
    
    # 1. Vérifier l'utilisateur admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Utilisateur admin trouvé: {admin_user.username}")
        print(f"   - is_superuser: {admin_user.is_superuser}")
        print(f"   - is_staff: {admin_user.is_staff}")
    except User.DoesNotExist:
        print("❌ Utilisateur admin non trouvé")
        return
    
    # 2. Vérifier le profil admin
    try:
        admin_profile = UserProfile.objects.get(user=admin_user)
        print(f"✅ Profil admin trouvé: {admin_profile.role}")
    except UserProfile.DoesNotExist:
        print("❌ Profil admin non trouvé")
        return
    
    # 3. Générer un token JWT
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    print(f"✅ Token JWT généré")
    
    # 4. Tester l'API getCurrentUser
    print("\n🔍 TEST API /auth/user/")
    print("-" * 30)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('http://localhost:8000/api/auth/user/', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Données utilisateur reçues:")
            print(f"   - Username: {user_data.get('username')}")
            print(f"   - Email: {user_data.get('email')}")
            print(f"   - is_superuser: {user_data.get('is_superuser')}")
            print(f"   - is_staff: {user_data.get('is_staff')}")
            print(f"   - Profile role: {user_data.get('profile', {}).get('role')}")
            print(f"   - Profile phone: {user_data.get('profile', {}).get('phone')}")
            print(f"   - Profile country: {user_data.get('profile', {}).get('country')}")
            
            # Vérifier la structure attendue par le frontend
            print("\n🔍 VÉRIFICATION STRUCTURE FRONTEND")
            print("-" * 35)
            
            required_fields = ['username', 'email', 'is_superuser', 'is_staff', 'profile']
            missing_fields = []
            
            for field in required_fields:
                if field not in user_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Champs manquants: {missing_fields}")
            else:
                print("✅ Tous les champs requis sont présents")
            
            # Vérifier le profil
            profile = user_data.get('profile', {})
            required_profile_fields = ['role', 'phone', 'country']
            missing_profile_fields = []
            
            for field in required_profile_fields:
                if field not in profile:
                    missing_profile_fields.append(field)
            
            if missing_profile_fields:
                print(f"❌ Champs profil manquants: {missing_profile_fields}")
            else:
                print("✅ Tous les champs profil requis sont présents")
            
            # Test de détection du rôle
            print("\n🔍 TEST DÉTECTION RÔLE")
            print("-" * 25)
            
            if user_data.get('is_superuser'):
                detected_role = 'super_admin'
            elif user_data.get('profile', {}).get('role'):
                detected_role = user_data.get('profile', {}).get('role')
            elif user_data.get('is_staff'):
                detected_role = 'organizer'
            else:
                detected_role = 'participant'
            
            print(f"Rôle détecté: {detected_role}")
            
            if detected_role == 'super_admin':
                print("✅ Super admin correctement détecté !")
            else:
                print(f"❌ Problème de détection du rôle: {detected_role}")
                
        else:
            print(f"❌ Erreur API: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # 5. Instructions pour le test frontend
    print("\n🔍 INSTRUCTIONS POUR LE TEST FRONTEND")
    print("-" * 40)
    print("1. Déployez le backend avec les corrections")
    print("2. Allez sur votre frontend Vercel")
    print("3. Connectez-vous avec admin / admin123")
    print("4. Vérifiez que vous voyez 'Super Administrateur' dans le profil")
    print("5. Vérifiez que vous avez accès au dashboard admin")

if __name__ == "__main__":
    test_frontend_connection()
