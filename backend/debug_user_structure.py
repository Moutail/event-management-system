#!/usr/bin/env python
"""
Debug de la structure complète de l'utilisateur
"""

import os
import sys
import django
from dotenv import load_dotenv
import json

# Charger les variables d'environnement
load_dotenv()

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

def debug_user_structure():
    """Debug de la structure complète de l'utilisateur"""
    print("🔍 Debug de la structure complète de l'utilisateur")
    print("=" * 70)
    
    username = 'lol1dov7'
    
    try:
        user = User.objects.get(username=username)
        print(f"\n👤 Utilisateur: {username}")
        print(f"   Email: {user.email}")
        print(f"   is_active: {user.is_active}")
        print(f"   is_staff: {user.is_staff}")
        print(f"   is_superuser: {user.is_superuser}")
        
        # Vérifier le profil
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"\n📋 Profil trouvé: Oui")
            print(f"   Rôle: {profile.role}")
            
            # Afficher tous les attributs du profil
            print(f"\n🔍 Tous les attributs du profil:")
            for field in profile._meta.fields:
                value = getattr(profile, field.name)
                print(f"   {field.name}: {value}")
                
        except UserProfile.DoesNotExist:
            print(f"\n❌ Profil trouvé: Non")
            
        # Vérifier les permissions
        print(f"\n🔐 Vérification des permissions:")
        print(f"   user.is_staff: {user.is_staff}")
        print(f"   user.is_superuser: {user.is_superuser}")
        
        if hasattr(user, 'profile'):
            print(f"   user.profile existe: Oui")
            if hasattr(user.profile, 'role'):
                print(f"   user.profile.role: {user.profile.role}")
            else:
                print(f"   user.profile.role: N'existe pas")
        else:
            print(f"   user.profile existe: Non")
            
        # Test de la logique d'autorisation
        print(f"\n🧮 Test de la logique d'autorisation:")
        isOrganizer = user.is_staff or user.is_superuser or (hasattr(user, 'profile') and hasattr(user.profile, 'role') and user.profile.role == 'organizer')
        print(f"   isOrganizer: {isOrganizer}")
        
        if isOrganizer:
            print(f"   ✅ ACCÈS AUTORISÉ")
        else:
            print(f"   ❌ ACCÈS REFUSÉ")
            
    except User.DoesNotExist:
        print(f"\n❌ Utilisateur {username} non trouvé")
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_user_structure()














