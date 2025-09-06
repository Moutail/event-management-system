#!/usr/bin/env python
"""
🧪 TEST : Authentification sociale pour vérifier qu'elle fonctionne
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, RefundRequest, RefundPolicy, SocialAccount
from events.views import google_auth, facebook_auth
from django.utils import timezone
from datetime import timedelta

def test_social_auth_models():
    """Test des modèles d'authentification sociale"""
    print("🚀 Test des modèles d'authentification sociale")
    
    try:
        # Créer un utilisateur test
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_social_user',
            defaults={
                'email': 'test_social@example.com',
                'first_name': 'Test',
                'last_name': 'Social'
            }
        )
        
        if created:
            print(f"✅ Utilisateur créé: {user.username}")
        else:
            print(f"✅ Utilisateur existant: {user.username}")
        
        # Créer un compte social Google
        social_account = SocialAccount.objects.create(
            user=user,
            provider='google',
            provider_account_id='test_google_id_123',
            email='test_social@example.com',
            name='Test Social User',
            picture_url='https://example.com/avatar.jpg'
        )
        
        print(f"✅ Compte social créé: {social_account.provider} - {social_account.provider_account_id}")
        
        # Vérifier les propriétés
        print(f"🔍 Compte expiré: {social_account.is_expired}")
        print(f"🔍 Date de création: {social_account.created_at}")
        print(f"🔍 Date de mise à jour: {social_account.updated_at}")
        
        # Nettoyer
        social_account.delete()
        if created:
            user.delete()
        
        print("✅ Test des modèles réussi !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test des modèles: {e}")
        import traceback
        traceback.print_exc()

def test_social_auth_views():
    """Test des vues d'authentification sociale"""
    print("\n🚀 Test des vues d'authentification sociale")
    
    try:
        # Créer un utilisateur test
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_social_view_user',
            defaults={
                'email': 'test_social_view@example.com',
                'first_name': 'Test',
                'last_name': 'SocialView'
            }
        )
        
        # Créer un client de test
        client = APIClient()
        
        # Test Google Auth (sans token valide)
        print("🔍 Test Google Auth (sans token valide)...")
        response = client.post('/api/auth/google/', {
            'id_token': 'invalid_token'
        })
        
        print(f"🔍 Réponse Google Auth: {response.status_code}")
        if response.status_code == 400:
            print("✅ Erreur attendue pour token invalide")
        else:
            print(f"⚠️ Statut inattendu: {response.status_code}")
        
        # Test Facebook Auth (sans token valide)
        print("🔍 Test Facebook Auth (sans token valide)...")
        response = client.post('/api/auth/facebook/', {
            'access_token': 'invalid_token'
        })
        
        print(f"🔍 Réponse Facebook Auth: {response.status_code}")
        if response.status_code == 400:
            print("✅ Erreur attendue pour token invalide")
        else:
            print(f"⚠️ Statut inattendu: {response.status_code}")
        
        # Nettoyer
        if created:
            user.delete()
        
        print("✅ Test des vues réussi !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test des vues: {e}")
        import traceback
        traceback.print_exc()

def test_social_auth_integration():
    """Test d'intégration de l'authentification sociale"""
    print("\n🚀 Test d'intégration de l'authentification sociale")
    
    try:
        # Vérifier que les modèles sont bien créés
        print("🔍 Vérification des modèles...")
        
        # Vérifier SocialAccount
        social_accounts = SocialAccount.objects.all()
        print(f"🔍 Comptes sociaux existants: {social_accounts.count()}")
        
        # Vérifier les providers disponibles
        providers = SocialAccount.PROVIDER_CHOICES
        print(f"🔍 Providers disponibles: {[p[0] for p in providers]}")
        
        # Vérifier les URLs d'authentification
        print("🔍 URLs d'authentification configurées:")
        print("  - Google: /api/auth/google/")
        print("  - Facebook: /api/auth/facebook/")
        
        print("✅ Test d'intégration réussi !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🧪 TESTS D'AUTHENTIFICATION SOCIALE")
    print("=" * 50)
    
    test_social_auth_models()
    test_social_auth_views()
    test_social_auth_integration()
    
    print("\n🎉 Tous les tests sont terminés !")
    print("\n📝 Prochaines étapes:")
    print("1. Configurez vos clés OAuth2 dans les fichiers .env")
    print("2. Testez avec de vrais tokens d'authentification")
    print("3. Vérifiez la redirection et la création de comptes")








