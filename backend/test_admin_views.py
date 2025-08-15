#!/usr/bin/env python
"""
Test des vues admin_views après correction
"""
import os
import django
import traceback

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from events.models import UserProfile
from events.admin_views import platform_analytics, pending_moderation

def test_admin_views():
    """Tester les vues admin_views après correction"""
    print("🔍 Test des vues admin_views après correction...")
    
    factory = RequestFactory()
    
    try:
        # 1. Créer un utilisateur authentifié
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Test de la vue platform_analytics
        print(f"\n🚀 Test 1: Vue platform_analytics...")
        try:
            request = factory.get('/admin/analytics/')
            request.user = super_admin
            response = platform_analytics(request)
            print(f"   ✅ platform_analytics fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                data = response.data
                print(f"   📊 Données retournées: {len(data)} sections")
        except Exception as e:
            print(f"   ❌ Erreur dans platform_analytics: {e}")
            traceback.print_exc()
        
        # 3. Test de la vue pending_moderation
        print(f"\n📋 Test 2: Vue pending_moderation...")
        try:
            request = factory.get('/admin/moderation/')
            request.user = super_admin
            response = pending_moderation(request)
            print(f"   ✅ pending_moderation fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                data = response.data
                print(f"   📊 Données retournées: {len(data)} sections")
        except Exception as e:
            print(f"   ❌ Erreur dans pending_moderation: {e}")
            traceback.print_exc()
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
    
    print("\n🎯 Test des vues admin_views terminé!")

if __name__ == '__main__':
    test_admin_views()
