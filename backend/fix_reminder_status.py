#!/usr/bin/env python
"""
🔧 CORRECTION DU STATUT DES RAPPELS
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

def fix_reminder_status():
    """Corriger le statut des rappels"""
    print("🔧 CORRECTION DU STATUT DES RAPPELS")
    print("=" * 60)
    
    # Récupérer les rappels en brouillon avec une heure programmée
    draft_with_schedule = CustomReminder.objects.filter(
        status='draft',
        scheduled_at__isnull=False
    )
    
    print(f"📊 Rappels à corriger: {draft_with_schedule.count()}")
    print()
    
    if draft_with_schedule.count() == 0:
        print("✅ Aucun rappel à corriger!")
        return
    
    # Corriger le statut
    updated_count = 0
    for reminder in draft_with_schedule:
        print(f"🔧 Correction du rappel ID {reminder.id}: {reminder.title}")
        print(f"   Heure programmée: {reminder.scheduled_at}")
        print(f"   Statut: {reminder.status} → scheduled")
        
        # Mettre à jour le statut
        reminder.status = 'scheduled'
        reminder.save()
        updated_count += 1
        
        print(f"   ✅ Statut mis à jour!")
        print()
    
    print(f"🎉 {updated_count} rappel(s) corrigé(s)!")
    print()
    
    # Vérifier le résultat
    scheduled_count = CustomReminder.objects.filter(status='scheduled').count()
    print(f"📊 Rappels programmés maintenant: {scheduled_count}")
    
    if scheduled_count > 0:
        print("✅ Le système de rappels automatiques va maintenant traiter ces rappels!")
        print("💡 Vérifiez les logs pour voir l'envoi automatique.")

if __name__ == "__main__":
    fix_reminder_status()
