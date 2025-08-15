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
from events.models import Event, EventRegistration, UserProfile, RefundRequest, NotificationLog
from django.utils import timezone

def create_test_data():
    """Créer des données de test pour le Super Admin"""
    print("🚀 Création des données de test...")
    
    # Créer des utilisateurs de test
    users_data = [
        {'username': 'organizer1', 'email': 'org1@test.com', 'role': 'organizer'},
        {'username': 'organizer2', 'email': 'org2@test.com', 'role': 'organizer'},
        {'username': 'participant1', 'email': 'part1@test.com', 'role': 'participant'},
        {'username': 'participant2', 'email': 'part2@test.com', 'role': 'participant'},
        {'username': 'participant3', 'email': 'part3@test.com', 'role': 'participant'},
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['username'].title(),
                'last_name': 'Test',
                'is_active': True
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            print(f"✅ Utilisateur créé: {user.username}")
        
        # Créer ou mettre à jour le profil
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': user_data['role'],
                'phone': f'06{random.randint(10000000, 99999999)}'
            }
        )
        
        if profile_created:
            print(f"✅ Profil créé pour {user.username} avec le rôle: {profile.role}")
        
        created_users.append(user)
    
    # Créer des événements de test
    events_data = [
        {
            'title': 'Conférence Tech 2025',
            'description': 'Une conférence sur les dernières technologies',
            'start_date': timezone.now() + timedelta(days=30),
            'end_date': timezone.now() + timedelta(days=30, hours=8),
            'location': 'Paris, France',
            'max_participants': 100,
            'price': 50.00,
            'status': 'published'
        },
        {
            'title': 'Workshop Développement Web',
            'description': 'Apprenez à créer des sites web modernes',
            'start_date': timezone.now() + timedelta(days=15),
            'end_date': timezone.now() + timedelta(days=15, hours=6),
            'location': 'Lyon, France',
            'max_participants': 25,
            'price': 75.00,
            'status': 'draft'
        },
        {
            'title': 'Meetup Entrepreneurs',
            'description': 'Réseautage et partage d\'expériences',
            'start_date': timezone.now() + timedelta(days=7),
            'end_date': timezone.now() + timedelta(days=7, hours=3),
            'location': 'Marseille, France',
            'max_participants': 50,
            'price': 0.00,
            'status': 'published'
        }
    ]
    
    created_events = []
    organizers = [u for u in created_users if u.profile.role == 'organizer']
    
    for i, event_data in enumerate(events_data):
        organizer = organizers[i % len(organizers)]
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            defaults={
                'description': event_data['description'],
                'start_date': event_data['start_date'],
                'end_date': event_data['end_date'],
                'location': event_data['location'],
                'max_participants': event_data['max_participants'],
                'price': event_data['price'],
                'status': event_data['status'],
                'organizer': organizer,
                'access_type': 'public'
            }
        )
        
        if created:
            print(f"✅ Événement créé: {event.title}")
        
        created_events.append(event)
    
    # Créer des inscriptions de test
    participants = [u for u in created_users if u.profile.role == 'participant']
    
    for event in created_events:
        if event.status == 'published':
            # Inscrire quelques participants
            for i, participant in enumerate(participants[:random.randint(1, 3)]):
                registration, created = EventRegistration.objects.get_or_create(
                    event=event,
                    user=participant,
                    defaults={
                        'status': 'confirmed',
                        'price_paid': event.price,
                        'registration_date': timezone.now() - timedelta(days=random.randint(1, 10))
                    }
                )
                
                if created:
                    print(f"✅ Inscription créée: {participant.username} -> {event.title}")
    
    # Créer des demandes de remboursement de test
    registrations = EventRegistration.objects.filter(status='confirmed')
    
    for registration in registrations[:2]:  # Créer 2 demandes de remboursement
        refund, created = RefundRequest.objects.get_or_create(
            registration=registration,
            defaults={
                'status': 'pending',
                'reason': 'Changement de plans',
                'amount_paid': registration.price_paid,
                'refund_percentage': 100,
                'refund_amount': registration.price_paid,
                'expires_at': timezone.now() + timedelta(days=7)
            }
        )
        
        if created:
            print(f"✅ Demande de remboursement créée pour {registration.user.username}")
    
    # Créer des notifications de test
    for event in created_events:
        notification, created = NotificationLog.objects.get_or_create(
            event=event,
            type='reminder_1d',
            defaults={
                'created_at': timezone.now() - timedelta(hours=random.randint(1, 24))
            }
        )
        
        if created:
            print(f"✅ Notification créée pour {event.title}")
    
    print("\n🎉 Données de test créées avec succès !")
    print("\n📊 Résumé:")
    print(f"   👥 Utilisateurs: {User.objects.count()}")
    print(f"   🎪 Événements: {Event.objects.count()}")
    print(f"   📝 Inscriptions: {EventRegistration.objects.count()}")
    print(f"   💰 Demandes de remboursement: {RefundRequest.objects.count()}")
    print(f"   🔔 Notifications: {NotificationLog.objects.count()}")
    
    print("\n🔑 Identifiants de test:")
    print("   Super Admin: window7 / (votre mot de passe)")
    print("   Organisateur: organizer1 / test123")
    print("   Participant: participant1 / test123")

if __name__ == '__main__':
    create_test_data()
