#!/usr/bin/env python
"""
Debug qui simule exactement ce que fait le serveur HTTP
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
from events.views import super_admin_global_stats
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

def debug_http_simulation():
    """Debug qui simule exactement ce que fait le serveur HTTP"""
    print("🔍 Debug qui simule exactement ce que fait le serveur HTTP...")
    
    try:
        # 1. Créer un utilisateur authentifié
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Générer un token JWT comme le fait le serveur
        print(f"\n🔑 Génération du token JWT...")
        try:
            refresh = RefreshToken.for_user(super_admin)
            access_token = str(refresh.access_token)
            print(f"   ✅ Token JWT généré: {access_token[:20]}...")
        except Exception as e:
            print(f"   ❌ Erreur génération token: {e}")
            traceback.print_exc()
            return
        
        # 3. Créer un client API avec le token comme le fait le serveur
        print(f"\n🚀 Test avec APIClient (comme le serveur HTTP)...")
        try:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            
            # Test de l'API avec authentification JWT
            response = client.get('/api/admin/global_stats/')
            print(f"   📊 Status de l'API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.data
                print(f"   🎉 SUCCÈS ! Données reçues: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
                print(f"   💰 Total revenus: {data.get('total_revenue', 'N/A')}")
            elif response.status_code == 500:
                print(f"   ❌ Erreur 500: {response.data}")
                if 'error' in response.data:
                    print(f"   📄 Message d'erreur: {response.data['error']}")
            else:
                print(f"   ❓ Status inattendu: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur dans l'API: {e}")
            traceback.print_exc()
            return
        
        # 4. Test direct de la vue (comme avant)
        print(f"\n🧪 Test direct de la vue (comme avant)...")
        try:
            factory = RequestFactory()
            request = factory.get('/admin/global_stats/')
            request.user = super_admin
            response = super_admin_global_stats(request)
            print(f"   ✅ Vue directe fonctionne - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur dans la vue directe: {e}")
            traceback.print_exc()
            return
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
    
    print("\n🎯 Debug HTTP simulation terminé!")

if __name__ == '__main__':
    debug_http_simulation()
