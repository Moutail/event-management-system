#!/usr/bin/env python
"""
Script pour nettoyer les données de test de la base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Category, Tag, Event, EventRegistration, EventHistory

def clear_sample_data():
    print("Nettoyage des données de test...")
    
    # Supprimer les inscriptions
    registrations_count = EventRegistration.objects.count()
    EventRegistration.objects.all().delete()
    print(f"{registrations_count} inscriptions supprimées")
    
    # Supprimer l'historique
    history_count = EventHistory.objects.count()
    EventHistory.objects.all().delete()
    print(f"{history_count} entrées d'historique supprimées")
    
    # Supprimer les événements
    events_count = Event.objects.count()
    Event.objects.all().delete()
    print(f"{events_count} événements supprimés")
    
    # Supprimer les tags
    tags_count = Tag.objects.count()
    Tag.objects.all().delete()
    print(f"{tags_count} tags supprimés")
    
    # Supprimer les catégories
    categories_count = Category.objects.count()
    Category.objects.all().delete()
    print(f"{categories_count} catégories supprimées")
    
    # Supprimer les utilisateurs de test (sauf admin)
    test_users = User.objects.filter(username__startswith='testuser')
    test_users_count = test_users.count()
    test_users.delete()
    print(f"{test_users_count} utilisateurs de test supprimés")
    
    print("\nNettoyage terminé!")
    print(f"Utilisateurs restants: {User.objects.count()}")
    print(f"Catégories restantes: {Category.objects.count()}")
    print(f"Tags restants: {Tag.objects.count()}")
    print(f"Événements restants: {Event.objects.count()}")
    print(f"Inscriptions restantes: {EventRegistration.objects.count()}")

if __name__ == '__main__':
    clear_sample_data() 