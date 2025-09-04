#!/usr/bin/env python
"""
Vérification des permissions des utilisateurs
"""

import os
import sys
import django
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def check_user_permissions():
    """Vérifie les permissions des utilisateurs"""
    print("🔍 Vérification des permissions des utilisateurs")
    print("=" * 60)
    
    # Utilisateurs à vérifier
    usernames = ['ameyodov7', 'lol1dov7', 'lol3dov7']
    
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            print(f"\n👤 Utilisateur: {username}")
            print(f"   Email: {user.email}")
            print(f"   Date de création: {user.date_joined}")
            print(f"   Dernière connexion: {user.last_login}")
            print(f"   is_active: {user.is_active}")
            print(f"   is_staff: {user.is_staff}")
            print(f"   is_superuser: {user.is_superuser}")
            
            # Vérifier le profil
            try:
                profile = UserProfile.objects.get(user=user)
                print(f"   Profil trouvé: Oui")
                print(f"   Rôle: {profile.role}")
                print(f"   Bio: {profile.bio[:50] if profile.bio else 'Aucune'}...")
            except UserProfile.DoesNotExist:
                print(f"   Profil trouvé: Non")
            
            # Vérifier les permissions
            print(f"   Permissions:")
            print(f"     - Peut accéder au générateur IA: {user.is_staff or user.is_superuser}")
            
            if user.is_staff or user.is_superuser:
                print(f"     ✅ ACCÈS AUTORISÉ")
            else:
                print(f"     ❌ ACCÈS REFUSÉ")
                
        except User.DoesNotExist:
            print(f"\n❌ Utilisateur {username} non trouvé")
        except Exception as e:
            print(f"\n❌ Erreur pour {username}: {str(e)}")

if __name__ == '__main__':
    check_user_permissions()
