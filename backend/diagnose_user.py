#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def diagnose_user():
    """Diagnostiquer le problème avec nealdov7"""
    print("🔍 DIAGNOSTIC UTILISATEUR nealdov7")
    print("=" * 50)
    
    try:
        # 1. Récupérer l'utilisateur
        user = User.objects.get(username='nealdov7')
        print(f"👤 Utilisateur trouvé: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Prénom: {user.first_name}")
        print(f"   Nom: {user.last_name}")
        print(f"   Date création: {user.date_joined}")
        print(f"   Dernière connexion: {user.last_login}")
        print()
        
        # 2. Vérifier les permissions
        print("🔐 PERMISSIONS :")
        print(f"   is_superuser: {user.is_superuser}")
        print(f"   is_staff: {user.is_staff}")
        print(f"   is_active: {user.is_active}")
        print()
        
        # 3. Vérifier les groupes
        print("👥 GROUPES :")
        groups = user.groups.all()
        if groups:
            for group in groups:
                print(f"   - {group.name}")
        else:
            print("   Aucun groupe")
        print()
        
        # 4. Vérifier les permissions individuelles
        print("🔑 PERMISSIONS INDIVIDUELLES :")
        permissions = user.user_permissions.all()
        if permissions:
            for perm in permissions:
                print(f"   - {perm.codename}")
        else:
            print("   Aucune permission individuelle")
        print()
        
        # 5. Vérifier l'authentification
        print("🔐 AUTHENTIFICATION :")
        auth_user = authenticate(username='nealdov7', password='test123')
        if auth_user:
            print(f"   ✅ Authentification réussie")
            print(f"   is_superuser (auth): {auth_user.is_superuser}")
            print(f"   is_staff (auth): {auth_user.is_staff}")
        else:
            print("   ❌ Authentification échouée")
        print()
        
        # 6. Comparer avec d'autres utilisateurs
        print("👥 COMPARAISON AVEC D'AUTRES UTILISATEURS :")
        all_users = User.objects.all()
        for u in all_users:
            if u.is_superuser:
                print(f"   🔴 {u.username}: SUPER ADMIN")
            elif u.is_staff:
                print(f"   🟡 {u.username}: STAFF")
            else:
                print(f"   ⚪ {u.username}: UTILISATEUR NORMAL")
        
    except User.DoesNotExist:
        print("❌ Utilisateur 'nealdov7' non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    diagnose_user()


