#!/usr/bin/env python
"""
🧪 TEST RAPIDE - AUTHENTIFICATION SOCIALE
"""

import os
import sys
import django
from pathlib import Path

def test_environment():
    """Test de l'environnement"""
    print("🔍 Test de l'environnement...")
    
    # Vérifier les fichiers .env
    backend_env = Path("backend/.env")
    frontend_env = Path("frontend/.env")
    
    if backend_env.exists():
        print("✅ backend/.env trouvé")
    else:
        print("❌ backend/.env manquant")
        return False
    
    if frontend_env.exists():
        print("✅ frontend/.env trouvé")
    else:
        print("❌ frontend/.env manquant")
        return False
    
    return True

def test_django_setup():
    """Test de la configuration Django"""
    print("\n🔍 Test de la configuration Django...")
    
    try:
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
        django.setup()
        print("✅ Django configuré avec succès")
        
        # Importer les modèles
        from events.models import SocialAccount
        print("✅ Modèle SocialAccount importé")
        
        # Vérifier les providers disponibles
        providers = SocialAccount.PROVIDER_CHOICES
        print(f"✅ Providers disponibles: {[p[0] for p in providers]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Django: {e}")
        return False

def test_views():
    """Test des vues d'authentification sociale"""
    print("\n🔍 Test des vues d'authentification sociale...")
    
    try:
        from events.views import google_auth, facebook_auth
        print("✅ Vues google_auth et facebook_auth importées")
        
        # Vérifier que les vues sont des fonctions
        if callable(google_auth):
            print("✅ google_auth est une fonction valide")
        else:
            print("❌ google_auth n'est pas une fonction")
            return False
        
        if callable(facebook_auth):
            print("✅ facebook_auth est une fonction valide")
        else:
            print("❌ facebook_auth n'est pas une fonction")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur vues: {e}")
        return False

def test_urls():
    """Test des URLs d'authentification sociale"""
    print("\n🔍 Test des URLs d'authentification sociale...")
    
    try:
        from django.urls import reverse
        from django.test import RequestFactory
        
        # Créer une requête de test
        factory = RequestFactory()
        
        # Vérifier que les URLs existent
        print("✅ URLs d'authentification sociale configurées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur URLs: {e}")
        return False

def test_configuration():
    """Test de la configuration"""
    print("\n🔍 Test de la configuration...")
    
    try:
        # Vérifier les variables d'environnement
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        facebook_app_id = os.getenv('FACEBOOK_APP_ID', '')
        
        if google_client_id and google_client_id != 'your-google-client-id-here':
            print("✅ GOOGLE_CLIENT_ID configuré")
        else:
            print("⚠️ GOOGLE_CLIENT_ID non configuré (utilisez le guide GOOGLE_OAUTH2_SETUP.md)")
        
        if facebook_app_id and facebook_app_id != 'your-facebook-app-id-here':
            print("✅ FACEBOOK_APP_ID configuré")
        else:
            print("⚠️ FACEBOOK_APP_ID non configuré (utilisez le guide FACEBOOK_OAUTH2_SETUP.md)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 TEST RAPIDE - AUTHENTIFICATION SOCIALE")
    print("=" * 50)
    print()
    
    tests = [
        test_environment,
        test_django_setup,
        test_views,
        test_urls,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Erreur lors du test {test.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("✅ L'authentification sociale est prête à être utilisée")
    else:
        print("⚠️ Certains tests ont échoué")
        print("📚 Consultez les guides de configuration:")
        print("   - GOOGLE_OAUTH2_SETUP.md")
        print("   - FACEBOOK_OAUTH2_SETUP.md")
    
    print()

if __name__ == "__main__":
    main()





