#!/usr/bin/env python3
"""
Vérification des mots de passe des utilisateurs
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User

def check_passwords():
    """Vérifie les mots de passe des utilisateurs"""
    print("=== VÉRIFICATION DES MOTS DE PASSE ===\n")
    
    try:
        # 1. Vérifier xchak475
        try:
            user1 = User.objects.get(username="xchak475")
            print(f"✅ Utilisateur: {user1.username}")
            print(f"   Email: {user1.email}")
            print(f"   Date de création: {user1.date_joined}")
            print(f"   Dernière connexion: {user1.last_login}")
            print(f"   Mot de passe défini: {'Oui' if user1.has_usable_password() else 'Non'}")
        except User.DoesNotExist:
            print(f"❌ Utilisateur xchak475 non trouvé")
        
        print()
        
        # 2. Vérifier nealdov7
        try:
            user2 = User.objects.get(username="nealdov7")
            print(f"✅ Utilisateur: {user2.username}")
            print(f"   Email: {user2.email}")
            print(f"   Date de création: {user2.date_joined}")
            print(f"   Dernière connexion: {user2.last_login}")
            print(f"   Mot de passe défini: {'Oui' if user2.has_usable_password() else 'Non'}")
        except User.DoesNotExist:
            print(f"❌ Utilisateur nealdov7 non trouvé")
        
        print()
        
        # 3. Créer un mot de passe pour xchak475 si nécessaire
        try:
            user1 = User.objects.get(username="xchak475")
            if not user1.has_usable_password():
                print("🔑 Création d'un mot de passe pour xchak475...")
                user1.set_password("test123")
                user1.save()
                print("   ✅ Mot de passe 'test123' créé")
            else:
                print("🔑 xchak475 a déjà un mot de passe")
        except User.DoesNotExist:
            print("❌ Impossible de créer le mot de passe pour xchak475")
        
        print()
        
        # 4. Créer un mot de passe pour nealdov7 si nécessaire
        try:
            user2 = User.objects.get(username="nealdov7")
            if not user2.has_usable_password():
                print("🔑 Création d'un mot de passe pour nealdov7...")
                user2.set_password("test123")
                user2.save()
                print("   ✅ Mot de passe 'test123' créé")
            else:
                print("🔑 nealdov7 a déjà un mot de passe")
        except User.DoesNotExist:
            print("❌ Impossible de créer le mot de passe pour nealdov7")
        
        print("\n=== RÉSULTAT ===")
        print("✅ Mots de passe vérifiés et créés si nécessaire")
        print("🔑 Utilisez 'test123' pour vous connecter")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_passwords()
