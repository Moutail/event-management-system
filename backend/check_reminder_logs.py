#!/usr/bin/env python
"""
📋 VÉRIFICATION DES LOGS DES RAPPELS
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import CustomReminder
from django.utils import timezone

def check_reminder_logs():
    """Vérifier les logs des rappels"""
    print("📋 VÉRIFICATION DES LOGS DES RAPPELS")
    print("=" * 60)
    
    # Récupérer tous les rappels récents
    recent_reminders = CustomReminder.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).order_by('-created_at')
    
    print(f"📊 Rappels créés dans les dernières 24h: {recent_reminders.count()}")
    print()
    
    if recent_reminders.count() == 0:
        print("❌ Aucun rappel créé récemment!")
        return
    
    # Afficher les détails des rappels récents
    print("📋 RAPPELS RÉCENTS:")
    print("-" * 80)
    
    for reminder in recent_reminders[:10]:  # Limiter à 10
        print(f"ID: {reminder.id}")
        print(f"Titre: {reminder.title}")
        print(f"Événement: {reminder.event.title}")
        print(f"Statut: {reminder.status}")
        print(f"Créé le: {reminder.created_at}")
        print(f"Heure programmée: {reminder.scheduled_at}")
        print(f"Email: {'✅' if reminder.send_email else '❌'}")
        print(f"SMS: {'✅' if reminder.send_sms else '❌'}")
        print(f"Audience: {reminder.target_audience}")
        print("-" * 80)
    
    # Vérifier les statuts
    print("\n📊 RÉPARTITION PAR STATUT:")
    print("-" * 40)
    for status in ['draft', 'scheduled', 'sent', 'failed']:
        count = CustomReminder.objects.filter(status=status).count()
        print(f"{status.upper()}: {count}")
    
    # Vérifier les rappels qui devraient être programmés
    print("\n🔍 RAPPELS QUI DEVRAIENT ÊTRE PROGRAMMÉS:")
    print("-" * 50)
    
    # Rappels en brouillon avec une heure programmée
    draft_with_schedule = CustomReminder.objects.filter(
        status='draft',
        scheduled_at__isnull=False
    )
    
    print(f"Rappels en brouillon avec heure programmée: {draft_with_schedule.count()}")
    
    for reminder in draft_with_schedule:
        print(f"   - ID {reminder.id}: {reminder.title} (programmé à {reminder.scheduled_at})")
        print(f"     Statut: {reminder.status} (devrait être 'scheduled')")

if __name__ == "__main__":
    check_reminder_logs()
