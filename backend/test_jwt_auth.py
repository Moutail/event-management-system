#!/usr/bin/env python
"""
Test de l'authentification JWT pour identifier l'erreur 500
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

def test_jwt_auth():
    """Tester l'authentification JWT"""
    print("🔐 Test de l'authentification JWT...")
    
    try:
        # 1. Créer un utilisateur et générer un token JWT
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Générer un token JWT
        refresh = RefreshToken.for_user(super_admin)
        access_token = str(refresh.access_token)
        print(f"🔑 Token JWT généré: {access_token[:20]}...")
        
        # 3. Créer un client API avec le token
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 4. Tester l'API avec authentification JWT
        print(f"\n🚀 Test de l'API avec JWT...")
        try:
            response = client.get('/api/admin/global_stats/')
            print(f"   ✅ API fonctionne - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.data
                print(f"   📊 Données reçues: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
            elif response.status_code == 401:
                print(f"   🔒 Authentification échouée")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur dans l'API: {e}")
            traceback.print_exc()
            return
        
        # 5. Vérifier les permissions
        print(f"\n🔍 Vérification des permissions...")
        print(f"   - Utilisateur authentifié: {super_admin.is_authenticated}")
        print(f"   - Rôle: {profile.role}")
        print(f"   - is_super_admin: {profile.is_super_admin}")
        print(f"   - is_staff: {super_admin.is_staff}")
        print(f"   - is_superuser: {super_admin.is_superuser}")
        
    except User.DoesNotExist:
        print("❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_jwt_auth()
