#!/usr/bin/env python
"""
Script pour vérifier les données existantes dans la base
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, User

def check_data():
    """Vérifier les données existantes"""
    print("🔍 Vérification des données existantes...")
    
    # Utilisateurs
    users = User.objects.all()
    print(f"\n👥 Utilisateurs ({users.count()}):")
    for user in users[:5]:  # Afficher les 5 premiers
        print(f"  - {user.username} ({user.email}) - {user.first_name} {user.last_name}")
    
    # Événements
    events = Event.objects.all()
    print(f"\n🎪 Événements ({events.count()}):")
    for event in events[:5]:
        print(f"  - {event.title} - {event.status} - Organisateur: {event.organizer}")
    
    # Inscriptions
    registrations = EventRegistration.objects.all()
    print(f"\n📝 Inscriptions ({registrations.count()}):")
    for reg in registrations[:5]:
        print(f"  - ID: {reg.id} - User: {reg.user.username} - Event: {reg.event.title} - Status: {reg.status}")
    
    # Vérifier les inscriptions avec utilisateurs
    print(f"\n🔍 Inscriptions avec utilisateurs valides:")
    valid_regs = []
    for reg in registrations:
        if reg.user and reg.event:
            valid_regs.append(reg)
            print(f"  ✅ {reg.id}: {reg.user.username} -> {reg.event.title} ({reg.status})")
    
    if valid_regs:
        print(f"\n🎯 Inscription de test recommandée: {valid_regs[0].id}")
        return valid_regs[0]
    else:
        print("\n❌ Aucune inscription valide trouvée")
        return None

if __name__ == '__main__':
    check_data()
