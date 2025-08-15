#!/usr/bin/env python
"""
Test spécifique de la vue analytics
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
from events.views import super_admin_analytics

def test_analytics():
    """Tester la vue analytics"""
    print("🔍 Test spécifique de la vue analytics...")
    
    factory = RequestFactory()
    
    try:
        # 1. Créer un utilisateur authentifié
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Test de la vue analytics
        print(f"\n🚀 Test de la vue analytics...")
        try:
            request = factory.get('/admin/analytics_advanced/?period=month')
            request.user = super_admin
            response = super_admin_analytics(request)
            print(f"   ✅ Vue analytics fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                data = response.data
                print(f"   📊 Données retournées: {len(data)} sections")
                if 'summary' in data:
                    print(f"   📈 Résumé: {len(data['summary'])} champs")
                if 'daily_stats' in data:
                    print(f"   📅 Stats quotidiennes: {len(data['daily_stats'])} jours")
                if 'role_distribution' in data:
                    print(f"   👥 Distribution des rôles: {len(data['role_distribution'])} rôles")
                if 'top_revenue_events' in data:
                    print(f"   💰 Top événements: {len(data['top_revenue_events'])} événements")
        except Exception as e:
            print(f"   ❌ Erreur dans la vue analytics: {e}")
            print(f"   🔍 Traceback complet:")
            traceback.print_exc()
            return
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
    
    print("\n🎯 Test analytics terminé!")

if __name__ == '__main__':
    test_analytics()
