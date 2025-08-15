#!/usr/bin/env python
"""
Script pour créer un profil Super Admin
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def create_super_admin():
    """Créer un profil Super Admin pour l'utilisateur existant"""
    try:
        # Récupérer l'utilisateur créé
        user = User.objects.get(username='window7')
        
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
        print(f"🔑 Rôle: {profile.role}")
        
    except User.DoesNotExist:
        print("❌ Utilisateur 'window7' non trouvé")
        print("Créer d'abord un utilisateur avec: python manage.py createsuperuser")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    create_super_admin()
