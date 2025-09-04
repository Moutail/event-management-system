#!/usr/bin/env python3
"""
🎯 CRÉATION DE DONNÉES SUPPLÉMENTAIRES POUR TESTER LE ML
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, Category, Tag, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone

def create_more_test_data():
    print("🎯 Création de données supplémentaires pour le ML...")
    
    try:
        # Créer des catégories si elles n'existent pas
        categories = []
        category_names = ['Business', 'Culture', 'Sport', 'Technology', 'Education', 'Entertainment']
        for name in category_names:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
            if created:
                print(f"✅ Catégorie créée: {name}")
        
        # Créer des tags
        tags = []
        tag_names = ['workshop', 'conference', 'networking', 'training', 'seminar', 'meetup', 'webinar', 'course']
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)
            if created:
                print(f"✅ Tag créé: {name}")
        
        # Récupérer un utilisateur organisateur
        organizer = User.objects.filter(is_superuser=True).first()
        if not organizer:
            print("❌ Aucun utilisateur superadmin trouvé")
            return
        
        # Créer 50 événements passés avec des données variées
        events_created = 0
        for i in range(50):
            # Date passée aléatoire (entre 30 et 365 jours dans le passé)
            days_ago = random.randint(30, 365)
            start_date = timezone.now() - timedelta(days=days_ago)
            
            # Données aléatoires
            price = Decimal(str(random.choice([0, 10, 25, 50, 100, 150, 200, 300])))
            max_capacity = random.choice([10, 20, 50, 100, 200, 500])
            category = random.choice(categories)
            
            locations = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Lille', 'Nantes', 'Strasbourg', 'Montpellier']
            location = random.choice(locations)
            
            # Créer l'événement
            event = Event.objects.create(
                title=f"Événement Test ML {i+1}",
                description=f"Description de l'événement test {i+1} pour le machine learning",
                start_date=start_date,
                end_date=start_date + timedelta(hours=random.choice([1, 2, 3, 4])),
                location=location,
                price=price,
                max_capacity=max_capacity,
                organizer=organizer,
                category=category,
                status='published',
                created_at=start_date - timedelta(days=random.randint(1, 30))
            )
            
            # Ajouter des tags aléatoires
            event_tags = random.sample(tags, random.randint(0, 3))
            event.tags.set(event_tags)
            
            # Créer des inscriptions aléatoires
            num_registrations = random.randint(0, min(max_capacity, max_capacity * random.choice([0.2, 0.5, 0.8, 1.0, 1.2])))
            for j in range(int(num_registrations)):
                # Créer un utilisateur factice si nécessaire
                username = f"user_test_{i}_{j}"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f"{username}@test.com",
                        'first_name': f"User{i}",
                        'last_name': f"Test{j}"
                    }
                )
                
                # Créer l'inscription
                registration_date = start_date - timedelta(days=random.randint(1, 20))
                EventRegistration.objects.get_or_create(
                    event=event,
                    user=user,
                    defaults={
                        'registered_at': registration_date,
                        'status': 'confirmed',
                        'price_paid': price
                    }
                )
            
            events_created += 1
            if events_created % 10 == 0:
                print(f"✅ {events_created} événements créés...")
        
        print(f"🎉 {events_created} événements créés avec succès!")
        
        # Statistiques
        total_events = Event.objects.filter(start_date__lt=timezone.now()).count()
        total_registrations = EventRegistration.objects.count()
        print(f"📊 Total événements passés: {total_events}")
        print(f"📊 Total inscriptions: {total_registrations}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_more_test_data()
