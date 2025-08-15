#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

print("=== DEBUG URLs DRF ===")

from rest_framework.routers import DefaultRouter
from events.views import EventRegistrationViewSet

# Créer un router pour tester
router = DefaultRouter()
router.register(r'registrations', EventRegistrationViewSet, basename='registration')

print("🔍 URLs générées par le router:")
for pattern in router.urls:
    print(f"   Pattern: {pattern.pattern}")
    print(f"   Name: {getattr(pattern, 'name', 'Aucun')}")
    print(f"   Callback: {pattern.callback}")
    if hasattr(pattern.callback, 'actions'):
        print(f"   Actions: {pattern.callback.actions}")
    print("   ---")

# Vérifier spécifiquement l'action refund
viewset = EventRegistrationViewSet()
print(f"\n📋 Actions dans EventRegistrationViewSet:")
for attr_name in dir(viewset):
    attr = getattr(viewset, attr_name)
    if hasattr(attr, 'mapping'):
        print(f"   - {attr_name}: {attr.mapping}")

print("\n=== Test URL /registrations/11/refund/ ===")
from django.urls import resolve, reverse, NoReverseMatch
from django.http import Http404

try:
    # Essayer de résoudre l'URL
    resolved = resolve('/api/registrations/11/refund/')
    print(f"✅ URL résolue: {resolved}")
    print(f"   View: {resolved.func}")
    print(f"   Args: {resolved.args}")
    print(f"   Kwargs: {resolved.kwargs}")
except Exception as e:
    print(f"❌ Erreur résolution URL: {e}")

# Essayer de construire l'URL inverse
try:
    url = reverse('registration-refund', kwargs={'pk': 11})
    print(f"✅ URL inverse: {url}")
except NoReverseMatch as e:
    print(f"❌ Pas de reverse match pour 'registration-refund': {e}")

print("=== FIN DEBUG ===")



