#!/usr/bin/env python
"""
Test avec authentification réelle pour identifier l'erreur 500
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

def test_with_auth():
    """Tester avec authentification réelle"""
    print("🔐 Test avec authentification réelle...")
    
    factory = RequestFactory()
    
    try:
        # 1. Créer un utilisateur authentifié
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Créer une requête authentifiée
        request = factory.get('/admin/global_stats/')
        request.user = super_admin
        
        # 3. Vérifier que l'utilisateur est bien authentifié
        print(f"🔍 Vérification de l'authentification:")
        print(f"   - Utilisateur: {request.user.username}")
        print(f"   - Authentifié: {request.user.is_authenticated}")
        print(f"   - Rôle: {profile.role}")
        
        # 4. Appeler la vue avec authentification
        print(f"\n🚀 Test de la vue avec authentification...")
        try:
            response = super_admin_global_stats(request)
            print(f"   ✅ Vue fonctionne - Status: {response.status_code}")
            
            if hasattr(response, 'data'):
                data = response.data
                print(f"   📊 Données retournées: {len(data)} champs")
                print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
                print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
            else:
                print(f"   ❌ Pas de données dans la réponse")
                
        except Exception as e:
            print(f"   ❌ Erreur dans la vue: {e}")
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
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_with_auth()
