from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import UserProfile


class Command(BaseCommand):
    help = 'Créer un super admin'

    def handle(self, *args, **options):
        username = "admin"
        password = "admin123"
        email = "admin@eventmanagement.com"
        
        # Supprimer l'utilisateur s'il existe déjà
        try:
            existing_user = User.objects.get(username=username)
            existing_user.delete()
            self.stdout.write(f"✅ Ancien utilisateur {username} supprimé")
        except User.DoesNotExist:
            pass
        
        # Créer le super admin
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(f"✅ Super admin créé: {username}")
        
        # Créer le profil utilisateur
        try:
            profile = UserProfile.objects.get(user=user)
            profile.role = 'super_admin'
            profile.phone = '+1234567890'
            profile.country = 'FR'
            profile.save()
            self.stdout.write(f"✅ Profil super admin mis à jour")
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(
                user=user,
                role='super_admin',
                phone='+1234567890',
                country='FR'
            )
            self.stdout.write(f"✅ Profil super admin créé")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Super admin créé avec succès !\n'
                f'   👑 Username: {username}\n'
                f'   🔑 Password: {password}\n'
                f'   📧 Email: {email}\n'
                f'\n✅ Vous pouvez maintenant vous connecter !'
            )
        )
