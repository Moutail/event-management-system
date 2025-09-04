#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event
from django.utils import timezone

print("=== DEBUG ÉVÉNEMENT WINNER500 ===")

# Chercher l'événement
event = Event.objects.filter(title='WINNER500').first()
if event:
    print(f"✅ Événement trouvé: {event.title}")
    print(f"   ID: {event.id}")
    print(f"   Status: {event.status}")
    print(f"   Date: {event.start_date}")
    print(f"   Prix: {event.price}€")
    print(f"   Capacité: {event.max_capacity}")
    print(f"   Organisateur: {event.organizer.username}")
    print(f"   Créé le: {event.created_at}")
    print(f"   Modifié le: {event.updated_at}")
    
    # Vérifier si c'est "published"
    is_published = event.status == 'published'
    print(f"   Est publié: {is_published}")
    
    # Vérifier si c'est dans le futur
    is_future = event.start_date > timezone.now()
    print(f"   Dans le futur: {is_future}")
    
    # Afficher tous les champs importants
    print(f"   Description: {event.description[:50]}..." if event.description else "   Description: Aucune")
    print(f"   Lieu: {event.location}")
    print(f"   Catégorie: {event.category.name if event.category else 'Aucune'}")
    
else:
    print("❌ Événement WINNER500 non trouvé")
    
    # Lister les derniers événements créés
    print("\n📋 Derniers événements créés:")
    recent_events = Event.objects.all().order_by('-created_at')[:5]
    for e in recent_events:
        print(f"   - {e.title} (ID: {e.id}, Status: {e.status}, Date: {e.start_date})")

print("\n=== VÉRIFICATION API ENDPOINTS ===")

# Vérifier quels événements sont retournés par les différents endpoints
print("\n🔍 Événements 'upcoming' (à venir):")
upcoming = Event.objects.filter(
    status='published',
    start_date__gt=timezone.now()
).order_by('start_date')[:5]

for e in upcoming:
    print(f"   - {e.title} (Date: {e.start_date})")

print("\n🔍 Événements 'featured' (mis en avant):")
featured = Event.objects.filter(
    status='published',
    is_featured=True
).order_by('-created_at')[:5]

for e in featured:
    print(f"   - {e.title} (Featured: {e.is_featured})")

print("=== FIN DEBUG ===")






