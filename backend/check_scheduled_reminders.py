#!/usr/bin/env python
"""
🔍 VÉRIFICATION DES RAPPELS PROGRAMMÉS
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import CustomReminder
from django.utils import timezone

def check_scheduled_reminders():
    """Vérifier les rappels programmés"""
    print("🔍 VÉRIFICATION DES RAPPELS PROGRAMMÉS")
    print("=" * 60)
    
    # Récupérer tous les rappels programmés
    scheduled_reminders = CustomReminder.objects.filter(status='scheduled')
    
    print(f"📊 Nombre de rappels programmés: {scheduled_reminders.count()}")
    print()
    
    if scheduled_reminders.count() == 0:
        print("❌ Aucun rappel programmé trouvé!")
        print()
        print("💡 Pour programmer un rappel:")
        print("   1. Créez un rappel via l'interface")
        print("   2. Définissez l'heure d'envoi")
        print("   3. Le statut doit être 'scheduled'")
        return
    
    # Afficher les détails des rappels programmés
    now = timezone.now()
    print("📋 RAPPELS PROGRAMMÉS:")
    print("-" * 60)
    
    for reminder in scheduled_reminders:
        time_diff = reminder.scheduled_at - now
        minutes_until = int(time_diff.total_seconds() / 60)
        
        print(f"ID: {reminder.id}")
        print(f"Titre: {reminder.title}")
        print(f"Événement: {reminder.event.title}")
        print(f"Heure programmée: {reminder.scheduled_at}")
        print(f"Statut: {reminder.status}")
        print(f"Minutes restantes: {minutes_until}")
        print(f"Email: {'✅' if reminder.send_email else '❌'}")
        print(f"SMS: {'✅' if reminder.send_sms else '❌'}")
        print("-" * 60)
    
    # Vérifier les rappels en retard
    overdue_reminders = scheduled_reminders.filter(scheduled_at__lt=now)
    if overdue_reminders.count() > 0:
        print(f"⚠️  {overdue_reminders.count()} rappel(s) en retard!")
        for reminder in overdue_reminders:
            print(f"   - ID {reminder.id}: {reminder.title} (programmé à {reminder.scheduled_at})")

if __name__ == "__main__":
    check_scheduled_reminders()
