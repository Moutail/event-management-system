#!/usr/bin/env python
"""
Test de l'API des remboursements
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from events.models import UserProfile, RefundRequest, EventRegistration, Event
from events.views import super_admin_refunds_list

def test_refunds_api():
    """Tester l'API des remboursements"""
    print("🧪 Test de l'API des remboursements...")
    
    # Créer un utilisateur de test
    factory = RequestFactory()
    
    try:
        # 1. Vérifier que le Super Admin existe
        super_admin = User.objects.get(username='window7')
        profile = UserProfile.objects.get(user=super_admin)
        print(f"   ✅ Super Admin trouvé: {super_admin.username} (rôle: {profile.role})")
        
        # 2. Vérifier qu'il y a des remboursements en base
        refunds_count = RefundRequest.objects.count()
        print(f"   📊 Remboursements en base: {refunds_count}")
        
        if refunds_count > 0:
            # Afficher quelques exemples
            for refund in RefundRequest.objects.all()[:3]:
                print(f"      - ID: {refund.id}, Status: {refund.status}, Montant: {refund.amount_paid}")
        
        # 3. Tester l'API
        request = factory.get('/refunds/')
        request.user = super_admin
        response = super_admin_refunds_list(request)
        
        print(f"   🔍 Test API - Status: {response.status_code}")
        if hasattr(response, 'data'):
            data = response.data
            print(f"      📊 Données retournées: {len(data)} champs")
            if 'results' in data:
                print(f"      📝 Remboursements: {len(data['results'])}")
                print(f"      📄 Total: {data['count']}")
            else:
                print(f"      ❌ Structure incorrecte: {list(data.keys())}")
        else:
            print(f"      ❌ Pas de données dans la réponse")
        
    except User.DoesNotExist:
        print("   ❌ Super Admin 'window7' non trouvé")
    except UserProfile.DoesNotExist:
        print("   ❌ Profil Super Admin non trouvé")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_refunds_api()
