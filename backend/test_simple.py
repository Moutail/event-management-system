#!/usr/bin/env python
"""
Test simple des APIs Super Admin
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from events.models import UserProfile
from events.views import super_admin_global_stats, super_admin_analytics

def test_apis():
    """Tester les APIs sans serveur"""
    print("🧪 Test des APIs Super Admin...")
    
    # Créer un utilisateur de test
    factory = RequestFactory()
    
    # 1. Tester l'API des statistiques globales
    print("\n📊 Test API Statistiques Globales...")
    try:
        request = factory.get('/admin/global_stats/')
        request.user = User.objects.get(username='window7')
        response = super_admin_global_stats(request)
        print(f"   ✅ API fonctionne - Status: {response.status_code}")
        print(f"   📊 Données: {len(response.data)} champs")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 2. Tester l'API Analytics
    print("\n📈 Test API Analytics...")
    try:
        request = factory.get('/admin/analytics_advanced/?period=month')
        request.user = User.objects.get(username='window7')
        response = super_admin_analytics(request)
        print(f"   ✅ API fonctionne - Status: {response.status_code}")
        print(f"   📊 Données: {len(response.data)} sections")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_apis()
