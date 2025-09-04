#!/usr/bin/env python
"""
Script pour créer un utilisateur de test avec un mot de passe connu
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def create_test_user():
    """Créer un utilisateur de test avec un mot de passe connu"""
    try:
        # Créer l'utilisateur
        user, created = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'testadmin@example.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': False
            }
        )
        
        if created:
            # Définir le mot de passe
            user.set_password('test123')
            user.save()
            print(f"✅ Utilisateur créé: {user.username}")
        else:
            # Mettre à jour le mot de passe
            user.set_password('test123')
            user.save()
            print(f"✅ Mot de passe mis à jour pour: {user.username}")
        
        # Créer ou mettre à jour le profil
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'super_admin',
                'phone': ''
            }
        )
        
        if created:
            print(f"✅ Profil Super Admin créé pour {user.username}")
        else:
            profile.role = 'super_admin'
            profile.save()
            print(f"✅ Profil Super Admin mis à jour pour {user.username}")
            
        print(f"👑 Utilisateur: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Mot de passe: test123")
        print(f"🔑 Rôle: {profile.role}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    create_test_user()
