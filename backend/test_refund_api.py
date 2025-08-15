#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.views import EventRegistrationViewSet
from rest_framework.request import Request
from django.test import RequestFactory

print("=== TEST API PROCESS_REFUND ===")

# Vérifier que la méthode existe
viewset = EventRegistrationViewSet()
print(f"✅ Méthode process_refund existe: {hasattr(viewset, 'process_refund')}")

# Vérifier les actions disponibles
from rest_framework.decorators import action

# Parcourir toutes les méthodes de la classe
actions = []
for method_name in dir(EventRegistrationViewSet):
    if not method_name.startswith('_'):
        try:
            method = getattr(EventRegistrationViewSet, method_name)
            if hasattr(method, 'mapping'):
                # C'est une action DRF
                actions.append({
                    'name': method_name,
                    'mapping': method.mapping,
                    'detail': getattr(method, 'detail', None),
                    'url_path': getattr(method, 'url_path', method_name)
                })
        except:
            pass

print(f"\n🔍 Actions disponibles dans EventRegistrationViewSet:")
for action_info in actions:
    print(f"   - {action_info['name']}: {action_info['mapping']} (detail={action_info['detail']}, url={action_info['url_path']})")

# Vérifier spécifiquement process_refund
try:
    method = getattr(EventRegistrationViewSet, 'process_refund')
    print(f"\n📋 Détails de process_refund:")
    print(f"   - Mapping: {getattr(method, 'mapping', 'Aucun')}")
    print(f"   - Detail: {getattr(method, 'detail', 'Aucun')}")
    print(f"   - URL path: {getattr(method, 'url_path', 'Aucun')}")
except Exception as e:
    print(f"\n❌ Erreur avec process_refund: {e}")

print("=== FIN TEST ===")
