#!/usr/bin/env python
"""
Script simple pour créer un super admin
"""
import os
import sys
import django

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')

try:
    django.setup()
    
    from django.contrib.auth.models import User
    from events.models import UserProfile
    
    def create_superadmin():
        """Créer un super admin"""
        print("🔧 Création du super admin...")
        
        username = "admin"
        password = "admin123"
        email = "admin@eventmanagement.com"
        
        # Supprimer l'utilisateur s'il existe déjà
        try:
            existing_user = User.objects.get(username=username)
            existing_user.delete()
            print(f"✅ Ancien utilisateur {username} supprimé")
        except User.DoesNotExist:
            pass
        
        # Créer le super admin
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Super admin créé: {username}")
        
        # Créer le profil utilisateur
        try:
            profile = UserProfile.objects.get(user=user)
            profile.role = 'super_admin'
            profile.phone_number = '+1234567890'
            profile.bio = 'Super administrateur'
            profile.save()
            print(f"✅ Profil super admin mis à jour")
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                role='super_admin',
                phone_number='+1234567890',
                bio='Super administrateur'
            )
            print(f"✅ Profil super admin créé")
        
        print(f"\n🎯 Super admin créé avec succès !")
        print(f"   👑 Username: {username}")
        print(f"   🔑 Password: {password}")
        print(f"   📧 Email: {email}")
        print(f"\n✅ Vous pouvez maintenant vous connecter !")
        
        return True
        
    if __name__ == "__main__":
        create_superadmin()
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous d'être dans le répertoire backend et que Django est installé")
