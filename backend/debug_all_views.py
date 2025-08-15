#!/usr/bin/env python
"""
Debug de toutes les vues Super Admin pour identifier l'erreur
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
from events.views import super_admin_global_stats, super_admin_analytics, super_admin_refunds_list

def debug_all_views():
    """Debug de toutes les vues Super Admin"""
    print("🔍 Debug de toutes les vues Super Admin...")
    
    factory = RequestFactory()
    
    try:
        # 1. Créer un utilisateur authentifié
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Test de la vue global_stats
        print(f"\n🚀 Test 1: Vue global_stats...")
        try:
            request = factory.get('/admin/global_stats/')
            request.user = super_admin
            response = super_admin_global_stats(request)
            print(f"   ✅ global_stats fonctionne - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur dans global_stats: {e}")
            traceback.print_exc()
        
        # 3. Test de la vue analytics
        print(f"\n📊 Test 2: Vue analytics...")
        try:
            request = factory.get('/admin/analytics_advanced/?period=month')
            request.user = super_admin
            response = super_admin_analytics(request)
            print(f"   ✅ analytics fonctionne - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur dans analytics: {e}")
            traceback.print_exc()
        
        # 4. Test de la vue refunds
        print(f"\n💰 Test 3: Vue refunds...")
        try:
            request = factory.get('/refunds/')
            request.user = super_admin
            response = super_admin_refunds_list(request)
            print(f"   ✅ refunds fonctionne - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur dans refunds: {e}")
            traceback.print_exc()
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
    
    print("\n🎯 Debug de toutes les vues terminé!")

if __name__ == '__main__':
    debug_all_views()
