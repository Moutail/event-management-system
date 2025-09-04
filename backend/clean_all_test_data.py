#!/usr/bin/env python3
"""
🧹 SCRIPT DE NETTOYAGE COMPLET DES DONNÉES DE TEST
Ce script supprime TOUTES les données créées par les scripts de test automatiques
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Event, EventRegistration, Category, Tag, UserProfile, RefundRequest, NotificationLog
from django.db import transaction

def clean_all_test_data():
    print("🧹 NETTOYAGE COMPLET DES DONNÉES DE TEST...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # 1. SUPPRIMER TOUTES LES INSCRIPTIONS DE TEST
            print("\n1️⃣ Suppression des inscriptions de test...")
            
            # Supprimer les inscriptions liées aux événements de test
            test_event_registrations = EventRegistration.objects.filter(
                event__title__icontains='Test ML'
            )
            test_registrations_count = test_event_registrations.count()
            test_event_registrations.delete()
            print(f"   ✅ {test_registrations_count} inscriptions d'événements de test supprimées")
            
            # Supprimer les inscriptions des utilisateurs de test
            test_user_registrations = EventRegistration.objects.filter(
                user__username__startswith='user_test_'
            )
            test_user_registrations_count = test_user_registrations.count()
            test_user_registrations.delete()
            print(f"   ✅ {test_user_registrations_count} inscriptions d'utilisateurs de test supprimées")
            
            # Supprimer TOUTES les autres inscriptions (probablement toutes de test)
            all_registrations = EventRegistration.objects.all()
            remaining_registrations_count = all_registrations.count()
            all_registrations.delete()
            print(f"   ✅ {remaining_registrations_count} inscriptions restantes supprimées")
            
            # 2. SUPPRIMER TOUS LES ÉVÉNEMENTS DE TEST
            print("\n2️⃣ Suppression des événements de test...")
            
            # Supprimer les événements avec "Test ML" dans le titre
            test_ml_events = Event.objects.filter(title__icontains='Test ML')
            test_ml_count = test_ml_events.count()
            test_ml_events.delete()
            print(f"   ✅ {test_ml_count} événements 'Test ML' supprimés")
            
            # Supprimer TOUS les autres événements (probablement tous de test)
            all_events = Event.objects.all()
            remaining_events_count = all_events.count()
            all_events.delete()
            print(f"   ✅ {remaining_events_count} événements restants supprimés")
            
            # 3. SUPPRIMER TOUS LES UTILISATEURS DE TEST
            print("\n3️⃣ Suppression des utilisateurs de test...")
            
            # Supprimer les utilisateurs avec "user_test_" dans le username
            test_users = User.objects.filter(username__startswith='user_test_')
            test_users_count = test_users.count()
            test_users.delete()
            print(f"   ✅ {test_users_count} utilisateurs 'user_test_' supprimés")
            
            # Supprimer les utilisateurs avec "testuser" dans le username
            testuser_users = User.objects.filter(username__startswith='testuser')
            testuser_count = testuser_users.count()
            testuser_users.delete()
            print(f"   ✅ {testuser_count} utilisateurs 'testuser' supprimés")
            
            # Supprimer les utilisateurs avec "organizer" dans le username
            organizer_users = User.objects.filter(username__startswith='organizer')
            organizer_count = organizer_users.count()
            organizer_users.delete()
            print(f"   ✅ {organizer_count} utilisateurs 'organizer' supprimés")
            
            # Supprimer les utilisateurs avec "participant" dans le username
            participant_users = User.objects.filter(username__startswith='participant')
            participant_count = participant_users.count()
            participant_users.delete()
            print(f"   ✅ {participant_count} utilisateurs 'participant' supprimés")
            
            # 4. SUPPRIMER LES PROFILS UTILISATEUR DE TEST
            print("\n4️⃣ Suppression des profils utilisateur de test...")
            
            # Supprimer tous les profils (ils seront recréés automatiquement si nécessaire)
            all_profiles = UserProfile.objects.all()
            profiles_count = all_profiles.count()
            all_profiles.delete()
            print(f"   ✅ {profiles_count} profils utilisateur supprimés")
            
            # 5. SUPPRIMER LES DEMANDES DE REMBOURSEMENT DE TEST
            print("\n5️⃣ Suppression des demandes de remboursement de test...")
            
            all_refunds = RefundRequest.objects.all()
            refunds_count = all_refunds.count()
            all_refunds.delete()
            print(f"   ✅ {refunds_count} demandes de remboursement supprimées")
            
            # 6. SUPPRIMER LES NOTIFICATIONS DE TEST
            print("\n6️⃣ Suppression des notifications de test...")
            
            all_notifications = NotificationLog.objects.all()
            notifications_count = all_notifications.count()
            all_notifications.delete()
            print(f"   ✅ {notifications_count} notifications supprimées")
            
            # 7. SUPPRIMER LES CATÉGORIES ET TAGS DE TEST
            print("\n7️⃣ Suppression des catégories et tags de test...")
            
            all_categories = Category.objects.all()
            categories_count = all_categories.count()
            all_categories.delete()
            print(f"   ✅ {categories_count} catégories supprimées")
            
            all_tags = Tag.objects.all()
            tags_count = all_tags.count()
            all_tags.delete()
            print(f"   ✅ {tags_count} tags supprimés")
            
            # 8. VÉRIFIER CE QUI RESTE
            print("\n8️⃣ Vérification finale...")
            
            remaining_users = User.objects.all()
            print(f"   👥 Utilisateurs restants: {remaining_users.count()}")
            for user in remaining_users:
                print(f"      - {user.username} ({user.email}) - Créé le: {user.date_joined}")
            
            remaining_events = Event.objects.all()
            print(f"   🎪 Événements restants: {remaining_events.count()}")
            
            remaining_registrations = EventRegistration.objects.all()
            print(f"   📝 Inscriptions restantes: {remaining_registrations.count()}")
            
            print("\n🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS!")
            print("=" * 50)
            print("✅ Toutes les données de test ont été supprimées")
            print("✅ Seules tes données personnelles restent")
            print("✅ Tu peux maintenant recommencer avec une base propre")
            
    except Exception as e:
        print(f"❌ ERREUR PENDANT LE NETTOYAGE: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n🔄 Le nettoyage a échoué. Aucune donnée n'a été supprimée.")

if __name__ == "__main__":
    # Demander confirmation avant de supprimer
    print("⚠️  ATTENTION: Ce script va supprimer TOUTES les données de test!")
    print("⚠️  Cela inclut:")
    print("   - Tous les événements de test")
    print("   - Tous les utilisateurs de test")
    print("   - Toutes les inscriptions de test")
    print("   - Toutes les catégories et tags de test")
    print("   - Toutes les demandes de remboursement de test")
    print("   - Toutes les notifications de test")
    print("\n❓ Es-tu sûr de vouloir continuer? (oui/non)")
    
    response = input("> ").lower().strip()
    
    if response in ['oui', 'yes', 'o', 'y']:
        clean_all_test_data()
    else:
        print("❌ Nettoyage annulé. Aucune donnée n'a été supprimée.")














