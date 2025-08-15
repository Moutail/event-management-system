#!/usr/bin/env python
"""
Test complet de toutes les APIs Super Admin
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from events.models import UserProfile, RefundRequest, Event, Category, Tag
from events.views import (
    super_admin_global_stats, 
    super_admin_analytics, 
    super_admin_refunds_list,
    categories_list,
    tags_list
)

def test_all_apis():
    """Tester toutes les APIs Super Admin"""
    print("🧪 Test complet de toutes les APIs Super Admin...")
    
    factory = RequestFactory()
    
    try:
        # 1. Vérifier que le Super Admin existe
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Tester l'API des statistiques globales
        print("\n📊 Test API Statistiques Globales...")
        try:
            request = factory.get('/admin/global_stats/')
            request.user = super_admin
            response = super_admin_global_stats(request)
            print(f"   ✅ API fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                data = response.data
                print(f"      📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"      🎪 Total événements: {data.get('total_events', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 3. Tester l'API Analytics
        print("\n📈 Test API Analytics...")
        try:
            request = factory.get('/admin/analytics_advanced/?period=month')
            request.user = super_admin
            response = super_admin_analytics(request)
            print(f"   ✅ API fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data') and 'summary' in response.data:
                summary = response.data['summary']
                print(f"      👥 Total utilisateurs: {summary.get('total_platform_users', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 4. Tester l'API des remboursements
        print("\n💰 Test API Remboursements...")
        try:
            request = factory.get('/refunds/')
            request.user = super_admin
            response = super_admin_refunds_list(request)
            print(f"   ✅ API fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data') and 'results' in response.data:
                data = response.data
                print(f"      📝 Remboursements: {len(data['results'])} / {data['count']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 5. Tester l'API des catégories
        print("\n📂 Test API Catégories...")
        try:
            request = factory.get('/categories_management/')
            request.user = super_admin
            response = categories_list(request)
            print(f"   ✅ API fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"      📂 Catégories: {len(response.data)}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 6. Tester l'API des tags
        print("\n🏷️  Test API Tags...")
        try:
            request = factory.get('/tags_management/')
            request.user = super_admin
            response = tags_list(request)
            print(f"   ✅ API fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"      🏷️  Tags: {len(response.data)}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # 7. Résumé des données en base
        print("\n📊 Résumé des données en base:")
        print(f"   👥 Utilisateurs: {User.objects.count()}")
        print(f"   🎪 Événements: {Event.objects.count()}")
        print(f"   💰 Remboursements: {RefundRequest.objects.count()}")
        print(f"   📂 Catégories: {Category.objects.count()}")
        print(f"   🏷️  Tags: {Tag.objects.count()}")
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_all_apis()
