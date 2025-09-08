#!/usr/bin/env python
"""
Test des imports pour vérifier que tout fonctionne
"""
import os
import sys
import django

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings_render')
django.setup()

try:
    from events.views.cron_views import trigger_notifications, health_check
    print("✅ Import cron_views réussi")
except ImportError as e:
    print(f"❌ Erreur import cron_views: {e}")

try:
    from events.management.commands.send_notifications_cron import Command
    print("✅ Import send_notifications_cron réussi")
except ImportError as e:
    print(f"❌ Erreur import send_notifications_cron: {e}")

print("✅ Test des imports terminé")
