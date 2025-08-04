#!/usr/bin/env python
"""
Script pour insérer des données de test dans la base de données
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Category, Tag, Event, EventRegistration, EventHistory

def create_sample_data():
    print("Création des données de test...")
    
    # Créer un utilisateur de test si il n'existe pas
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"Utilisateur créé: {user.username}")
    else:
        print(f"Utilisateur existant: {user.username}")
    
    # Créer des catégories
    categories_data = [
        {'name': 'Conférence', 'description': 'Événements de conférence et séminaires'},
        {'name': 'Concert', 'description': 'Concerts et spectacles musicaux'},
        {'name': 'Formation', 'description': 'Sessions de formation et ateliers'},
        {'name': 'Exposition', 'description': 'Expositions d\'art et galeries'},
        {'name': 'Sport', 'description': 'Événements sportifs et compétitions'},
        {'name': 'Technologie', 'description': 'Événements tech et innovation'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories[cat_data['name']] = category
        if created:
            print(f"Catégorie créée: {category.name}")
    
    # Créer des tags
    tags_data = [
        'Gratuit', 'Payant', 'En ligne', 'Présentiel', 'Premium', 'Débutant', 
        'Avancé', 'Networking', 'Innovation', 'Art', 'Musique', 'Business', 'Technologie', 'Sport'
    ]
    
    tags = {}
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags[tag_name] = tag
        if created:
            print(f"Tag créé: {tag.name}")
    
    # Créer des événements
    events_data = [
        {
            'title': 'Conférence sur l\'Intelligence Artificielle',
            'description': 'Une conférence passionnante sur les dernières avancées en IA',
            'category': categories['Conférence'],
            'tags': [tags['Technologie'], tags['Innovation'], tags['Payant']],
            'start_date': datetime.now() + timedelta(days=15),
            'end_date': datetime.now() + timedelta(days=15, hours=4),
            'location': 'Centre de Congrès, Paris',
            'max_capacity': 200,
            'place_type': 'limited',
            'price': Decimal('50.00'),
            'status': 'published',
            'is_featured': True,
            'organizer': user
        },
        {
            'title': 'Concert Jazz en Plein Air',
            'description': 'Une soirée jazz exceptionnelle sous les étoiles',
            'category': categories['Concert'],
            'tags': [tags['Musique'], tags['Gratuit'], tags['Présentiel']],
            'start_date': datetime.now() + timedelta(days=7),
            'end_date': datetime.now() + timedelta(days=7, hours=3),
            'location': 'Parc de la Villette, Paris',
            'max_capacity': 500,
            'place_type': 'limited',
            'price': Decimal('0.00'),
            'status': 'published',
            'is_featured': True,
            'organizer': user
        },
        {
            'title': 'Formation React Avancé',
            'description': 'Maîtrisez React avec des techniques avancées',
            'category': categories['Formation'],
            'tags': [tags['Technologie'], tags['Avancé'], tags['Payant'], tags['En ligne']],
            'start_date': datetime.now() + timedelta(days=10),
            'end_date': datetime.now() + timedelta(days=12),
            'location': 'En ligne (Zoom)',
            'max_capacity': 50,
            'place_type': 'limited',
            'price': Decimal('299.00'),
            'status': 'published',
            'is_featured': False,
            'organizer': user
        },
        {
            'title': 'Exposition d\'Art Contemporain',
            'description': 'Découvrez les œuvres d\'artistes contemporains émergents',
            'category': categories['Exposition'],
            'tags': [tags['Art'], tags['Gratuit'], tags['Présentiel']],
            'start_date': datetime.now() + timedelta(days=5),
            'end_date': datetime.now() + timedelta(days=20),
            'location': 'Galerie Moderne, Lyon',
            'max_capacity': 1000,
            'place_type': 'limited',
            'price': Decimal('0.00'),
            'status': 'published',
            'is_featured': False,
            'organizer': user
        },
        {
            'title': 'Marathon de Paris',
            'description': 'Participez au célèbre marathon de Paris',
            'category': categories['Sport'],
            'tags': [tags['Sport'], tags['Payant'], tags['Présentiel']],
            'start_date': datetime.now() + timedelta(days=30),
            'end_date': datetime.now() + timedelta(days=30, hours=6),
            'location': 'Champs-Élysées, Paris',
            'max_capacity': 50000,
            'place_type': 'limited',
            'price': Decimal('80.00'),
            'status': 'published',
            'is_featured': True,
            'organizer': user
        },
        {
            'title': 'Meetup Développeurs Web',
            'description': 'Rencontrez d\'autres développeurs et partagez vos expériences',
            'category': categories['Conférence'],
            'tags': [tags['Technologie'], tags['Networking'], tags['Gratuit'], tags['Présentiel']],
            'start_date': datetime.now() + timedelta(days=3),
            'end_date': datetime.now() + timedelta(days=3, hours=2),
            'location': 'Espace Coworking, Marseille',
            'max_capacity': 80,
            'place_type': 'limited',
            'price': Decimal('0.00'),
            'status': 'published',
            'is_featured': False,
            'organizer': user
        },
        {
            'title': 'Atelier Cuisine Française',
            'description': 'Apprenez à cuisiner les plats traditionnels français',
            'category': categories['Formation'],
            'tags': [tags['Débutant'], tags['Payant'], tags['Présentiel']],
            'start_date': datetime.now() + timedelta(days=8),
            'end_date': datetime.now() + timedelta(days=8, hours=4),
            'location': 'École de Cuisine, Bordeaux',
            'max_capacity': 20,
            'place_type': 'limited',
            'price': Decimal('120.00'),
            'status': 'published',
            'is_featured': False,
            'organizer': user
        },
        {
            'title': 'Conférence sur le Développement Durable',
            'description': 'Solutions innovantes pour un avenir plus vert',
            'category': categories['Conférence'],
            'tags': [tags['Innovation'], tags['Business'], tags['Gratuit'], tags['En ligne']],
            'start_date': datetime.now() + timedelta(days=12),
            'end_date': datetime.now() + timedelta(days=12, hours=3),
            'location': 'En ligne (Teams)',
            'max_capacity': 300,
            'place_type': 'limited',
            'price': Decimal('0.00'),
            'status': 'published',
            'is_featured': True,
            'organizer': user
        }
    ]
    
    for event_data in events_data:
        tags_list = event_data.pop('tags')
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            defaults=event_data
        )
        if created:
            event.tags.set(tags_list)
            print(f"Événement créé: {event.title}")
        else:
            print(f"Événement existant: {event.title}")
    
    # Créer quelques inscriptions
    test_users = []
    for i in range(1, 6):
        test_user, created = User.objects.get_or_create(
            username=f'testuser{i}',
            defaults={
                'email': f'testuser{i}@example.com',
                'first_name': f'Test{i}',
                'last_name': 'User'
            }
        )
        if created:
            test_user.set_password('test123')
            test_user.save()
        test_users.append(test_user)
    
    # Inscrire quelques utilisateurs aux événements
    events = Event.objects.filter(status='published')[:3]
    for i, event in enumerate(events):
        if i < len(test_users):
            registration, created = EventRegistration.objects.get_or_create(
                event=event,
                user=test_users[i],
                defaults={'status': 'confirmed'}
            )
            if created:
                print(f"Inscription créée: {test_users[i].username} -> {event.title}")
    
    print("\nDonnées de test créées avec succès!")
    print(f"Utilisateurs créés: {User.objects.count()}")
    print(f"Catégories créées: {Category.objects.count()}")
    print(f"Tags créés: {Tag.objects.count()}")
    print(f"Événements créés: {Event.objects.count()}")
    print(f"Inscriptions créées: {EventRegistration.objects.count()}")

if __name__ == '__main__':
    create_sample_data() 