#!/usr/bin/env python
"""
Script pour créer des données de test pour le Super Admin
"""
import os
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event, EventRegistration, UserProfile, RefundRequest, NotificationLog, Category, Tag

def create_test_data():
    """Créer des données de test complètes"""
    print("🚀 Création des données de test pour le Super Admin...")
    
    # 1. Créer des catégories
    print("\n📂 Création des catégories...")
    categories_data = [
        {'name': 'Technologie', 'description': 'Événements tech et innovation', 'color': '#1976d2', 'icon': '💻'},
        {'name': 'Business', 'description': 'Événements business et entrepreneuriat', 'color': '#2e7d32', 'icon': '💼'},
        {'name': 'Culture', 'description': 'Événements culturels et artistiques', 'color': '#ed6c02', 'icon': '🎭'},
        {'name': 'Sport', 'description': 'Événements sportifs et fitness', 'color': '#d32f2f', 'icon': '⚽'},
        {'name': 'Formation', 'description': 'Événements de formation et éducation', 'color': '#7b1fa2', 'icon': '📚'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"   ✅ Catégorie créée: {category.name}")
        else:
            print(f"   ℹ️  Catégorie existante: {category.name}")
    
    # 2. Créer des tags
    print("\n🏷️  Création des tags...")
    tags_data = [
        {'name': 'Conférence', 'color': '#d32f2f'},
        {'name': 'Workshop', 'color': '#7b1fa2'},
        {'name': 'Meetup', 'color': '#1976d2'},
        {'name': 'Formation', 'color': '#388e3c'},
        {'name': 'Networking', 'color': '#f57c00'},
        {'name': 'Gratuit', 'color': '#388e3c'},
        {'name': 'Payant', 'color': '#d32f2f'}
    ]
    
    tags = []
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults=tag_data
        )
        tags.append(tag)
        if created:
            print(f"   ✅ Tag créé: {tag.name}")
        else:
            print(f"   ℹ️  Tag existant: {tag.name}")
    
    # 3. Créer des utilisateurs de test
    print("\n👥 Création des utilisateurs de test...")
    
    # Vérifier si le Super Admin existe
    try:
        super_admin = User.objects.get(username='window7')
        super_admin_profile, created = UserProfile.objects.get_or_create(
            user=super_admin,
            defaults={'role': 'super_admin', 'phone': ''}
        )
        if created:
            print(f"   ✅ Profil Super Admin créé pour {super_admin.username}")
        else:
            super_admin_profile.role = 'super_admin'
            super_admin_profile.save()
            print(f"   ✅ Profil Super Admin mis à jour pour {super_admin.username}")
    except User.DoesNotExist:
        print("   ⚠️  Super Admin 'window7' non trouvé - créer d'abord avec createsuperuser")
    
    # Créer des organisateurs
    organizers_data = [
        {'username': 'organizer1', 'email': 'organizer1@example.com', 'first_name': 'Jean', 'last_name': 'Dupont'},
        {'username': 'organizer2', 'email': 'organizer2@example.com', 'first_name': 'Marie', 'last_name': 'Martin'},
        {'username': 'organizer3', 'email': 'organizer3@example.com', 'first_name': 'Pierre', 'last_name': 'Durand'}
    ]
    
    organizers = []
    for org_data in organizers_data:
        user, created = User.objects.get_or_create(
            username=org_data['username'],
            defaults={
                'email': org_data['email'],
                'first_name': org_data['first_name'],
                'last_name': org_data['last_name'],
                'is_active': True
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            print(f"   ✅ Organisateur créé: {user.username}")
        else:
            print(f"   ℹ️  Organisateur existant: {user.username}")
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'organizer', 'phone': f'+33 6 {random.randint(10000000, 99999999)}'}
        )
        organizers.append(user)
    
    # Créer des participants
    participants_data = [
        {'username': 'participant1', 'email': 'participant1@example.com', 'first_name': 'Alice', 'last_name': 'Bernard'},
        {'username': 'participant2', 'email': 'participant2@example.com', 'first_name': 'Bob', 'last_name': 'Petit'},
        {'username': 'participant3', 'email': 'participant3@example.com', 'first_name': 'Claire', 'last_name': 'Moreau'}
    ]
    
    participants = []
    for part_data in participants_data:
        user, created = User.objects.get_or_create(
            username=part_data['username'],
            defaults={
                'email': part_data['email'],
                'first_name': part_data['first_name'],
                'last_name': part_data['last_name'],
                'is_active': True
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            print(f"   ✅ Participant créé: {user.username}")
        else:
            print(f"   ℹ️  Participant existant: {user.username}")
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'participant', 'phone': f'+33 6 {random.randint(10000000, 99999999)}'}
        )
        participants.append(user)
    
    # 4. Créer des événements
    print("\n🎪 Création des événements...")
    
    event_titles = [
        'Conférence Tech 2025',
        'Workshop Développement Web',
        'Meetup Entrepreneurs',
        'Formation Marketing Digital',
        'Conférence IA & Machine Learning',
        'Workshop Design Thinking',
        'Meetup Développeurs',
        'Formation Leadership',
        'Conférence Innovation',
        'Workshop Gestion de Projet'
    ]
    
    events = []
    for i, title in enumerate(event_titles):
        # Choisir un organisateur aléatoire
        organizer = random.choice(organizers)
        
        # Choisir une catégorie aléatoire
        category = random.choice(categories)
        
        # Choisir des tags aléatoires
        event_tags = random.sample(tags, random.randint(1, 3))
        
        # Créer des dates aléatoires dans le futur
        start_date = timezone.now() + timedelta(days=random.randint(1, 90))
        end_date = start_date + timedelta(hours=random.randint(2, 8))
        
        # Statut aléatoire
        status_choices = ['draft', 'pending', 'published', 'cancelled']
        status = random.choice(status_choices)
        
        # Prix aléatoire
        is_free = random.choice([True, False])
        price = 0 if is_free else random.randint(10, 100)
        
        event = Event.objects.create(
            title=title,
            description=f"Description détaillée pour {title}. Un événement passionnant à ne pas manquer !",
            organizer=organizer,
            category=category,
            start_date=start_date,
            end_date=end_date,
            location=f"Lieu {i+1}, Ville {i+1}",
            max_capacity=random.randint(20, 200),
            price=price,
            is_free=is_free,
            status=status,
            place_type='limited'
        )
        
        # Ajouter les tags
        event.tags.set(event_tags)
        
        events.append(event)
        print(f"   ✅ Événement créé: {event.title} (Organisateur: {organizer.username})")
    
    # 5. Créer des inscriptions
    print("\n📝 Création des inscriptions...")
    
    for event in events:
        if event.status == 'published':
            # Nombre d'inscriptions aléatoire
            num_registrations = random.randint(0, min(event.max_capacity, 50))
            
            for _ in range(num_registrations):
                participant = random.choice(participants)
                
                # Vérifier si l'utilisateur n'est pas déjà inscrit
                if not EventRegistration.objects.filter(event=event, user=participant).exists():
                    registration = EventRegistration.objects.create(
                        event=event,
                        user=participant,
                        status=random.choice(['pending', 'confirmed', 'cancelled']),
                        price_paid=event.price if not event.is_free else 0
                    )
                    print(f"   ✅ Inscription créée: {participant.username} -> {event.title}")
    
    # 6. Créer des demandes de remboursement
    print("\n💰 Création des demandes de remboursement...")
    
    # Récupérer les inscriptions payantes confirmées
    paid_registrations = EventRegistration.objects.filter(
        price_paid__gt=0,
        status='confirmed'
    )[:5]  # Limiter à 5 demandes
    
    for registration in paid_registrations:
        refund_request, created = RefundRequest.objects.get_or_create(
            registration=registration,
            defaults={
                'reason': random.choice([
                    'Changement de plan',
                    'Problème de santé',
                    'Conflit d\'horaire',
                    'Autre raison personnelle'
                ]),
                'status': random.choice(['pending', 'approved', 'rejected']),
                'amount_paid': registration.price_paid,
                'refund_percentage': 100,
                'refund_amount': registration.price_paid,
                'expires_at': timezone.now() + timedelta(days=30)
            }
        )
        if created:
            print(f"   ✅ Demande de remboursement créée: {registration.user.username} -> {registration.event.title}")
        else:
            print(f"   ℹ️  Demande de remboursement existante: {registration.user.username} -> {registration.event.title}")
    
    # 7. Créer des notifications
    print("\n🔔 Création des notifications...")
    
    notification_types = ['registration_confirmed', 'event_reminder', 'event_cancelled', 'refund_approved']
    
    for user in participants + organizers:
        for _ in range(random.randint(1, 3)):
            # Choisir un événement aléatoire
            event = random.choice(events)
            # Choisir une inscription aléatoire pour cet utilisateur
            registration = EventRegistration.objects.filter(user=user, event=event).first()
            
            notification = NotificationLog.objects.create(
                event=event,
                registration=registration,
                type=random.choice(notification_types)
            )
    
    print("\n🎉 Données de test créées avec succès !")
    print("\n📊 Résumé:")
    print(f"   📂 Catégories: {Category.objects.count()}")
    print(f"   🏷️  Tags: {Tag.objects.count()}")
    print(f"   👥 Utilisateurs: {User.objects.count()}")
    print(f"   🎪 Événements: {Event.objects.count()}")
    print(f"   📝 Inscriptions: {EventRegistration.objects.count()}")
    print(f"   💰 Demandes de remboursement: {RefundRequest.objects.count()}")
    print(f"   🔔 Notifications: {NotificationLog.objects.count()}")
    
    print("\n🔑 Identifiants de test:")
    print("   Super Admin: window7 / (votre mot de passe)")
    print("   Organisateur: organizer1 / test123")
    print("   Participant: participant1 / test123")
    
    print("\n💡 Pour tester:")
    print("   1. Connectez-vous en tant que Super Admin")
    print("   2. Allez sur /super-admin")
    print("   3. Testez tous les onglets")

if __name__ == '__main__':
    create_test_data()
