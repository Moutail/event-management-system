#!/usr/bin/env python3
"""
Réinitialisation des mots de passe des utilisateurs
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User

def reset_passwords():
    """Réinitialise les mots de passe des utilisateurs"""
    print("=== RÉINITIALISATION DES MOTS DE PASSE ===\n")
    
    try:
        # 1. Réinitialiser xchak475
        try:
            user1 = User.objects.get(username="xchak475")
            user1.set_password("test123")
            user1.save()
            print(f"✅ Mot de passe réinitialisé pour {user1.username}: test123")
        except User.DoesNotExist:
            print(f"❌ Utilisateur xchak475 non trouvé")
        
        # 2. Réinitialiser nealdov7
        try:
            user2 = User.objects.get(username="nealdov7")
            user2.set_password("test123")
            user2.save()
            print(f"✅ Mot de passe réinitialisé pour {user2.username}: test123")
        except User.DoesNotExist:
            print(f"❌ Utilisateur nealdov7 non trouvé")
        
        print("\n=== RÉSULTAT ===")
        print("✅ Mots de passe réinitialisés à 'test123'")
        print("🔑 Vous pouvez maintenant vous connecter avec 'test123'")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_passwords()
