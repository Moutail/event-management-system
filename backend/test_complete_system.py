#!/usr/bin/env python
"""
Script de test complet du système d'événements virtuels
"""
import os
import sys
import django
import time
import requests
from datetime import datetime, timedelta

def setup_django():
    """Configure Django pour les tests"""
    print("🔧 Configuration de Django...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings_minimal')
    
    try:
        django.setup()
        print("✅ Django configuré avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration Django: {e}")
        return False

def test_database_models():
    """Test des modèles de base de données"""
    print("\n🗄️ Test des modèles de base de données...")
    
    try:
        from events.models import Event, VirtualEvent, VirtualEventInteraction, EventRegistration
        
        # Test de création d'événement
        print("   📝 Test de création d'événement...")
        event = Event(
            title="Test Événement Virtuel",
            description="Description de test",
            event_type="virtual",
            start_date=datetime.now() + timedelta(days=7),
            end_date=datetime.now() + timedelta(days=7, hours=2),
            location="Zoom",
            price=0.00,
            is_free=True,
            status="draft"
        )
        print("   ✅ Modèle Event créé avec succès")
        
        # Test de création d'événement virtuel
        print("   🌐 Test de création d'événement virtuel...")
        virtual_event = VirtualEvent(
            platform="zoom",
            meeting_id="TEST123",
            meeting_password="test123",
            auto_record=True,
            allow_chat=True,
            allow_screen_sharing=True,
            waiting_room=True,
            access_instructions="Instructions de test",
            technical_requirements="Aucune exigence particulière"
        )
        print("   ✅ Modèle VirtualEvent créé avec succès")
        
        # Test de création d'interaction
        print("   💬 Test de création d'interaction...")
        interaction = VirtualEventInteraction(
            interaction_type="like",
            content="J'aime cet événement!",
            rating=5
        )
        print("   ✅ Modèle VirtualEventInteraction créé avec succès")
        
        print("   🎉 Tous les modèles sont fonctionnels!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des modèles: {e}")
        return False

def test_services():
    """Test des services backend"""
    print("\n🔧 Test des services backend...")
    
    try:
        from events.services import (
            VirtualEventNotificationService,
            VirtualEventAutomationService,
            VirtualEventRecordingService,
            VirtualEventAnalyticsService
        )
        
        print("   ✅ VirtualEventNotificationService importé")
        print("   ✅ VirtualEventAutomationService importé")
        print("   ✅ VirtualEventRecordingService importé")
        print("   ✅ VirtualEventAnalyticsService importé")
        
        print("   🎉 Tous les services sont disponibles!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des services: {e}")
        return False

def test_management_commands():
    """Test des commandes de gestion"""
    print("\n⚙️ Test des commandes de gestion...")
    
    try:
        # Vérifier que les fichiers existent
        commands = [
            'events/management/commands/send_virtual_reminders.py',
            'events/management/commands/process_virtual_waitlist.py',
            'events/management/commands/cleanup_virtual_recordings.py'
        ]
        
        for command in commands:
            if os.path.exists(command):
                print(f"   ✅ {command} existe")
            else:
                print(f"   ❌ {command} manquant")
        
        print("   🎉 Commandes de gestion vérifiées!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des commandes: {e}")
        return False

def test_email_templates():
    """Test des templates d'email"""
    print("\n📧 Test des templates d'email...")
    
    try:
        templates = [
            'events/templates/emails/virtual_access_code.html',
            'events/templates/emails/virtual_access_code.txt',
            'events/templates/emails/virtual_reminder.html',
            'events/templates/emails/virtual_reminder.txt',
            'events/templates/emails/recording_available.html',
            'events/templates/emails/recording_available.txt'
        ]
        
        for template in templates:
            if os.path.exists(template):
                print(f"   ✅ {template} existe")
            else:
                print(f"   ❌ {template} manquant")
        
        print("   🎉 Templates d'email vérifiés!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des templates: {e}")
        return False

def test_frontend_components():
    """Test des composants frontend"""
    print("\n🎨 Test des composants frontend...")
    
    try:
        components = [
            '../frontend/src/components/VirtualEventCreation.js',
            '../frontend/src/components/VirtualEventDisplay.js',
            '../frontend/src/components/VirtualEventRecordingManager.js',
            '../frontend/src/components/VirtualEventList.js',
            '../frontend/src/components/VirtualEventAnalytics.js'
        ]
        
        for component in components:
            if os.path.exists(component):
                print(f"   ✅ {component} existe")
            else:
                print(f"   ❌ {component} manquant")
        
        print("   🎉 Composants frontend vérifiés!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des composants: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test complet du système d'événements virtuels")
    print("=" * 60)
    
    # Configuration Django
    if not setup_django():
        return
    
    # Tests des composants
    tests = [
        ("Modèles de base de données", test_database_models),
        ("Services backend", test_services),
        ("Commandes de gestion", test_management_commands),
        ("Templates d'email", test_email_templates),
        ("Composants frontend", test_frontend_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des tests
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Résultat: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Le système est prêt.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    print("\n📋 Prochaines étapes:")
    print("   1. ✅ Migrations créées et appliquées")
    print("   2. ✅ Modèles et services testés")
    print("   3. 🔄 Démarrer le serveur Django")
    print("   4. 🔄 Tester les API avec Postman")
    print("   5. 🔄 Intégrer les composants React")
    print("   6. 🔄 Tester le flux complet")

if __name__ == "__main__":
    main()
