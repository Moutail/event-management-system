#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User

def make_super_admin():
    """Rendre nealdov7 super admin"""
    try:
        # Chercher l'utilisateur nealdov7
        user = User.objects.get(username='nealdov7')
        
        print(f"🔍 Utilisateur trouvé: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Super admin actuel: {user.is_superuser}")
        print(f"   Staff actuel: {user.is_staff}")
        
        # Rendre super admin
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        print(f"✅ {user.username} est maintenant SUPER ADMIN !")
        print(f"   Super admin: {user.is_superuser}")
        print(f"   Staff: {user.is_staff}")
        
        # Vérifier tous les utilisateurs
        print("\n🔍 Statut de tous les utilisateurs :")
        print("=" * 40)
        for u in User.objects.all():
            status = []
            if u.is_superuser:
                status.append("SUPER ADMIN")
            if u.is_staff:
                status.append("STAFF")
            if u.is_active:
                status.append("ACTIF")
            else:
                status.append("INACTIF")
            print(f"👤 {u.username}: {' | '.join(status)}")
            
    except User.DoesNotExist:
        print("❌ Utilisateur 'nealdov7' non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    make_super_admin()


