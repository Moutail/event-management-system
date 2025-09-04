#!/usr/bin/env python
"""
Script pour vérifier l'état exact de l'utilisateur windov7
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def check_user_status():
    """Vérifier l'état de l'utilisateur windov7"""
    try:
        # Rechercher l'utilisateur
        user = User.objects.get(username='windov7')
        
        print(f"🔍 DIAGNOSTIC de l'utilisateur: {user.username}")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Prénom: {user.first_name}")
        print(f"   - Nom: {user.last_name}")
        print(f"   - is_superuser: {user.is_superuser}")
        print(f"   - is_staff: {user.is_staff}")
        print(f"   - is_active: {user.is_active}")
        print(f"   - Date création: {user.date_joined}")
        
        # Vérifier le profil
        try:
            profile = user.profile
            print(f"   - Profil trouvé: OUI")
            print(f"   - Rôle dans UserProfile: {profile.role}")
            print(f"   - Téléphone: {profile.phone}")
        except UserProfile.DoesNotExist:
            print(f"   - Profil trouvé: NON")
        
        # Vérifier les permissions
        print(f"\n🔐 PERMISSIONS:")
        print(f"   - Peut accéder à l'admin Django: {user.is_staff}")
        print(f"   - Est super admin Django: {user.is_superuser}")
        
        # Vérifier les groupes
        print(f"\n👥 GROUPES:")
        for group in user.groups.all():
            print(f"   - {group.name}")
        if not user.groups.exists():
            print(f"   - Aucun groupe")
            
    except User.DoesNotExist:
        print(f"❌ Utilisateur 'windov7' non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    check_user_status()


