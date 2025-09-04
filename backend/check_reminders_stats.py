#!/usr/bin/env python
"""
📊 VÉRIFICATION DES STATISTIQUES DES RAPPELS
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import CustomReminder

def check_reminders_stats():
    """Vérifier les statistiques des rappels"""
    print("📊 STATISTIQUES DES RAPPELS AUTOMATIQUES")
    print("=" * 60)
    
    # Statistiques générales
    total = CustomReminder.objects.count()
    scheduled = CustomReminder.objects.filter(status='scheduled').count()
    sent = CustomReminder.objects.filter(status='sent').count()
    draft = CustomReminder.objects.filter(status='draft').count()
    failed = CustomReminder.objects.filter(status='failed').count()
    
    print(f"📈 Total des rappels: {total}")
    print(f"⏰ Rappels programmés (scheduled): {scheduled}")
    print(f"✅ Rappels envoyés (sent): {sent}")
    print(f"📝 Rappels brouillons (draft): {draft}")
    print(f"❌ Rappels échoués (failed): {failed}")
    
    print("\n" + "=" * 60)
    print("📋 DERNIERS RAPPELS CRÉÉS (10 derniers)")
    print("=" * 60)
    
    # Derniers rappels créés
    recent_reminders = CustomReminder.objects.order_by('-id')[:10]
    
    for reminder in recent_reminders:
        print(f"ID: {reminder.id:3d} | Titre: {reminder.title[:30]:30s} | Statut: {reminder.status:10s} | Heure: {reminder.scheduled_at}")
    
    print("\n" + "=" * 60)
    print("🎯 RAPPELS PROGRAMMÉS EN ATTENTE")
    print("=" * 60)
    
    # Rappels programmés en attente
    pending_reminders = CustomReminder.objects.filter(status='scheduled').order_by('scheduled_at')
    
    if pending_reminders.exists():
        for reminder in pending_reminders:
            print(f"ID: {reminder.id:3d} | Titre: {reminder.title[:30]:30s} | Heure: {reminder.scheduled_at}")
    else:
        print("Aucun rappel programmé en attente")
    
    print("\n" + "=" * 60)
    print("✅ RAPPELS ENVOYÉS RÉCEMMENT")
    print("=" * 60)
    
    # Rappels envoyés récemment
    sent_reminders = CustomReminder.objects.filter(status='sent').order_by('-id')[:5]
    
    if sent_reminders.exists():
        for reminder in sent_reminders:
            print(f"ID: {reminder.id:3d} | Titre: {reminder.title[:30]:30s} | Heure: {reminder.scheduled_at}")
    else:
        print("Aucun rappel envoyé récemment")

if __name__ == "__main__":
    check_reminders_stats()
