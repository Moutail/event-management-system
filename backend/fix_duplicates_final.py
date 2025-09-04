#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import EventRegistration
from django.db.models import Count

def fix_duplicates():
    """Nettoie les doublons de téléphone"""
    print("🔧 Nettoyage des doublons de téléphone...")
    
    # Trouver les doublons
    duplicates = EventRegistration.objects.filter(
        guest_phone__isnull=False
    ).exclude(
        guest_phone=''
    ).values('event', 'guest_phone').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    print(f"📱 Trouvé {duplicates.count()} groupes de doublons")
    
    for duplicate in duplicates:
        event_id = duplicate['event']
        phone = duplicate['guest_phone']
        
        # Récupérer toutes les inscriptions avec ce téléphone pour cet événement
        registrations = list(EventRegistration.objects.filter(
            event_id=event_id,
            guest_phone=phone
        ).order_by('registered_at'))
        
        print(f"📱 Événement {event_id}, Téléphone {phone}: {len(registrations)} inscriptions")
        
        # Garder la première inscription, supprimer les autres
        first_registration = registrations[0]
        duplicates_to_delete = registrations[1:]
        
        print(f"🗑️ Suppression de {len(duplicates_to_delete)} doublons")
        for reg in duplicates_to_delete:
            print(f"   - Suppression: {reg.guest_full_name} ({reg.guest_email})")
            reg.delete()
    
    print("✅ Nettoyage terminé!")

if __name__ == '__main__':
    fix_duplicates()



