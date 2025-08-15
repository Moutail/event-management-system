#!/usr/bin/env python
"""
Debug détaillé de l'API pour identifier l'erreur 500
"""
import os
import django
import traceback

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from events.models import UserProfile, Event, EventRegistration
from events.views import super_admin_global_stats

def debug_api():
    """Debug détaillé de l'API"""
    print("🔍 Debug détaillé de l'API des statistiques globales...")
    
    factory = RequestFactory()
    
    try:
        # 1. Vérifier que le Super Admin existe
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Vérifier les données en base
        print(f"\n📊 Données en base:")
        print(f"   👥 Utilisateurs: {User.objects.count()}")
        print(f"   🎪 Événements: {Event.objects.count()}")
        print(f"   📝 Inscriptions: {EventRegistration.objects.count()}")
        
        # 3. Test étape par étape
        print(f"\n🧪 Test étape par étape...")
        
        # Test 1: Compter les utilisateurs
        try:
            total_users = User.objects.count()
            print(f"   ✅ Count users: {total_users}")
        except Exception as e:
            print(f"   ❌ Erreur count users: {e}")
            traceback.print_exc()
            return
        
        # Test 2: Compter les événements
        try:
            total_events = Event.objects.count()
            print(f"   ✅ Count events: {total_events}")
        except Exception as e:
            print(f"   ❌ Erreur count events: {e}")
            traceback.print_exc()
            return
        
        # Test 3: Compter les inscriptions
        try:
            total_registrations = EventRegistration.objects.count()
            print(f"   ✅ Count registrations: {total_registrations}")
        except Exception as e:
            print(f"   ❌ Erreur count registrations: {e}")
            traceback.print_exc()
            return
        
        # Test 4: Calculer les revenus
        try:
            from django.db.models import Sum
            total_revenue = EventRegistration.objects.aggregate(
                total=Sum('price_paid')
            )['total'] or 0
            print(f"   ✅ Calcul revenus: {total_revenue}")
        except Exception as e:
            print(f"   ❌ Erreur calcul revenus: {e}")
            traceback.print_exc()
            return
        
        # Test 5: Appeler la vue complète
        print(f"\n🚀 Test de la vue complète...")
        try:
            request = factory.get('/admin/global_stats/')
            request.user = super_admin
            response = super_admin_global_stats(request)
            print(f"   ✅ Vue fonctionne - Status: {response.status_code}")
            if hasattr(response, 'data'):
                data = response.data
                print(f"   📊 Données retournées: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erreur dans la vue: {e}")
            traceback.print_exc()
            return
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
    
    print("\n🎯 Debug terminé!")

if __name__ == '__main__':
    debug_api()
