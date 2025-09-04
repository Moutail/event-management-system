#!/usr/bin/env python
"""
🧪 TEST MANUEL DE LA VÉRIFICATION DES RAPPELS
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.tasks import check_scheduled_reminders
from events.models import CustomReminder
from django.utils import timezone

def test_manual_reminder_check():
    """Tester manuellement la vérification des rappels"""
    print("🧪 TEST MANUEL DE LA VÉRIFICATION DES RAPPELS")
    print("=" * 60)
    
    # Vérifier l'état avant
    scheduled_before = CustomReminder.objects.filter(status='scheduled').count()
    print(f"📊 Rappels programmés avant: {scheduled_before}")
    
    # Exécuter manuellement la tâche
    print("🚀 Exécution manuelle de check_scheduled_reminders()...")
    try:
        result = check_scheduled_reminders()
        print(f"✅ Tâche exécutée avec succès: {result}")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
    
    # Vérifier l'état après
    scheduled_after = CustomReminder.objects.filter(status='scheduled').count()
    sent_after = CustomReminder.objects.filter(status='sent').count()
    
    print(f"📊 Rappels programmés après: {scheduled_after}")
    print(f"📊 Rappels envoyés après: {sent_after}")
    
    # Vérifier les changements
    if scheduled_before > scheduled_after:
        print(f"🎉 {scheduled_before - scheduled_after} rappel(s) traité(s) automatiquement!")
    else:
        print("⚠️  Aucun rappel traité automatiquement")
    
    # Afficher les rappels en retard
    now = timezone.now()
    overdue_reminders = CustomReminder.objects.filter(
        status='scheduled',
        scheduled_at__lt=now
    )
    
    print(f"\n⏰ Rappels en retard: {overdue_reminders.count()}")
    for reminder in overdue_reminders:
        time_diff = now - reminder.scheduled_at
        hours_late = int(time_diff.total_seconds() / 3600)
        print(f"   - ID {reminder.id}: {reminder.title} ({hours_late}h de retard)")

if __name__ == "__main__":
    test_manual_reminder_check()
