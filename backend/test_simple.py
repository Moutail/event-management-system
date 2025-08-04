#!/usr/bin/env python
"""
Test simple pour vérifier la configuration Django
"""
import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

print("=== Test de configuration Django ===")
print(f"DEBUG: {settings.DEBUG}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")

# Vérifier si le dossier media existe
if os.path.exists(settings.MEDIA_ROOT):
    print(f"✅ Dossier MEDIA_ROOT existe: {settings.MEDIA_ROOT}")
else:
    print(f"❌ Dossier MEDIA_ROOT n'existe pas: {settings.MEDIA_ROOT}")

# Vérifier les permissions
try:
    test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("✅ Permissions d'écriture OK")
except Exception as e:
    print(f"❌ Problème de permissions: {e}")

print("=== Test terminé ===") 