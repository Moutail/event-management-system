#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.urls import reverse, resolve, NoReverseMatch

print("=== TEST URL PROCESS_REFUND ===")

# Test 1: Essayer de générer l'URL
try:
    url = reverse('process_refund', kwargs={'registration_id': 12})
    print(f"✅ URL générée: {url}")
except NoReverseMatch as e:
    print(f"❌ Erreur reverse: {e}")
except Exception as e:
    print(f"❌ Erreur générale: {e}")

# Test 2: Essayer de résoudre l'URL
try:
    resolved = resolve('/api/registrations/12/process_refund/')
    print(f"✅ URL résolue: {resolved}")
    print(f"   View: {resolved.func}")
    print(f"   Args: {resolved.args}")
    print(f"   Kwargs: {resolved.kwargs}")
except Exception as e:
    print(f"❌ Erreur résolution: {e}")

# Test 3: Lister toutes les URLs events
print("\n🔍 URLs dans events.urls:")
from django.conf import settings
from importlib import import_module

try:
    events_urls = import_module('events.urls')
    for pattern in events_urls.urlpatterns:
        print(f"   - {pattern.pattern} → {getattr(pattern, 'name', 'Aucun nom')}")
except Exception as e:
    print(f"❌ Erreur import events.urls: {e}")

print("=== FIN TEST ===")






