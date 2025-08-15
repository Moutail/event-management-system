#!/usr/bin/env python
"""
Script simple pour vérifier les données en base
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Event, EventRegistration, UserProfile, Category, Tag

def check_data():
    """Vérifier les données en base"""
    print("🔍 Vérification des données en base...")
    
    # 1. Vérifier les utilisateurs
    print(f"\n👥 Utilisateurs: {User.objects.count()}")
    for user in User.objects.all()[:5]:  # Afficher les 5 premiers
        try:
            profile = user.profile
            print(f"   - {user.username} ({user.email}) - Rôle: {profile.role} - Actif: {user.is_active}")
        except:
            print(f"   - {user.username} ({user.email}) - Pas de profil - Actif: {user.is_active}")
    
    # 2. Vérifier les événements
    print(f"\n🎪 Événements: {Event.objects.count()}")
    for event in Event.objects.all()[:5]:  # Afficher les 5 premiers
        print(f"   - {event.title} - Organisateur: {event.organizer.username} - Statut: {event.status}")
    
    # 3. Vérifier les inscriptions
    print(f"\n📝 Inscriptions: {EventRegistration.objects.count()}")
    
    # 4. Vérifier les catégories
    print(f"\n📂 Catégories: {Category.objects.count()}")
    for cat in Category.objects.all():
        print(f"   - {cat.name} ({cat.description})")
    
    # 5. Vérifier les tags
    print(f"\n🏷️  Tags: {Tag.objects.count()}")
    for tag in Tag.objects.all():
        print(f"   - {tag.name} ({tag.color})")
    
    # 6. Vérifier le Super Admin
    try:
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"\n👑 Super Admin: {super_admin.username} - Rôle: {profile.role}")
    except:
        print(f"\n❌ Super Admin 'window7' non trouvé ou pas de profil")

if __name__ == '__main__':
    check_data()
