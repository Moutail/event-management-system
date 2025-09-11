#!/usr/bin/env python
"""
Script pour créer un utilisateur de test pour l'authentification
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def create_test_user():
    """Créer un utilisateur de test pour l'authentification"""
    print("🔧 Création d'un utilisateur de test...")
    
    # Créer l'utilisateur admin s'il n'existe pas
    username = "admin"
    password = "admin123"
    email = "admin@test.com"
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Utilisateur {username} existe déjà")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Utilisateur {username} créé avec succès")
    
    # Créer le profil utilisateur
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"✅ Profil utilisateur existe déjà")
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            role='super_admin',
            phone_number='+1234567890',
            bio='Super administrateur de test'
        )
        print(f"✅ Profil utilisateur créé")
    
    # Créer aussi un utilisateur normal
    normal_username = "testuser"
    normal_password = "test123"
    
    try:
        normal_user = User.objects.get(username=normal_username)
        print(f"✅ Utilisateur {normal_username} existe déjà")
    except User.DoesNotExist:
        normal_user = User.objects.create_user(
            username=normal_username,
            email="test@test.com",
            password=normal_password
        )
        print(f"✅ Utilisateur {normal_username} créé avec succès")
        
        # Créer le profil
        try:
            normal_profile = UserProfile.objects.get(user=normal_user)
        except UserProfile.DoesNotExist:
            normal_profile = UserProfile.objects.create(
                user=normal_user,
                role='user',
                phone_number='+1234567891',
                bio='Utilisateur de test'
            )
            print(f"✅ Profil utilisateur normal créé")
    
    print("\n🎯 Utilisateurs de test créés :")
    print(f"   👑 Super Admin: {username} / {password}")
    print(f"   👤 Utilisateur: {normal_username} / {normal_password}")
    print("\n✅ Vous pouvez maintenant vous connecter avec ces identifiants !")

if __name__ == "__main__":
    create_test_user()