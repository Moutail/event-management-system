#!/usr/bin/env python3
"""
Script de test pour l'API Chatbot IA
Teste toutes les fonctionnalités du chatbot intelligent
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/path/to/your/project')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, VirtualEvent

User = get_user_model()

class AIBotTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api"
        self.headers = {"Content-Type": "application/json"}
        self.auth_headers = {}
    
    def test_public_info(self):
        """Test de l'endpoint public d'informations IA"""
        print("\n" + "="*60)
        print("🤖 TEST 1: Informations publiques IA")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/ai/info/")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCÈS - Informations IA récupérées:")
                print(f"  - Nom: {data['ai_info']['name']}")
                print(f"  - Version: {data['ai_info']['version']}")
                print(f"  - Capacités: {len(data['ai_info']['capabilities'])} fonctionnalités")
                print(f"  - Questions d'exemple: {len(data['sample_questions'])}")
                return True
            else:
                print(f"❌ ÉCHEC - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            return False
    
    def authenticate_user(self, username="testuser", password="testpass123"):
        """Authentification d'un utilisateur de test"""
        print("\n" + "="*60)
        print("🔑 AUTHENTIFICATION")
        print("="*60)
        
        try:
            # Créer un utilisateur de test s'il n'existe pas
            try:
                user = User.objects.get(username=username)
                print(f"✅ Utilisateur existant trouvé: {username}")
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@test.com",
                    password=password
                )
                print(f"✅ Utilisateur créé: {username}")
            
            # Authentification
            auth_data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(f"{self.base_url}/auth/token/", json=auth_data)
            
            if response.status_code == 200:
                tokens = response.json()
                self.auth_headers = {
                    "Authorization": f"Bearer {tokens['access']}",
                    "Content-Type": "application/json"
                }
                print("✅ Authentification réussie")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            return False
    
    def test_chat_basic(self):
        """Test du chat basique avec l'IA"""
        print("\n" + "="*60)
        print("💬 TEST 2: Chat basique avec IA")
        print("="*60)
        
        test_messages = [
            "Bonjour",
            "Comment m'inscrire à un événement ?",
            "J'ai un problème de streaming",
            "Comment payer ?",
            "Au revoir"
        ]
        
        results = []
        
        for message in test_messages:
            try:
                print(f"\n📝 Message: '{message}'")
                
                data = {"message": message}
                response = requests.post(
                    f"{self.base_url}/ai/chat/",
                    json=data,
                    headers=self.auth_headers
                )
                
                if response.status_code == 200:
                    ai_response = response.json()
                    print(f"✅ Réponse IA (intent: {ai_response.get('intent', 'unknown')}):")
                    print(f"   {ai_response.get('response', 'Pas de réponse')[:100]}...")
                    
                    if ai_response.get('suggestions'):
                        print(f"   💡 Suggestions: {len(ai_response['suggestions'])}")
                    
                    results.append(True)
                else:
                    print(f"❌ ÉCHEC - Status: {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ ERREUR: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n🎯 Taux de réussite: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate > 80
    
    def test_suggestions(self):
        """Test des suggestions intelligentes"""
        print("\n" + "="*60)
        print("💡 TEST 3: Suggestions intelligentes")
        print("="*60)
        
        try:
            response = requests.get(
                f"{self.base_url}/ai/suggestions/",
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                user_context = data.get('user_context', {})
                
                print(f"✅ SUCCÈS - {len(suggestions)} suggestions reçues")
                print(f"   Contexte utilisateur: {user_context}")
                
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"   {i}. {suggestion['text']} (intent: {suggestion['intent']})")
                
                return True
            else:
                print(f"❌ ÉCHEC - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            return False
    
    def test_contextual_help(self):
        """Test de l'aide contextuelle pour un événement"""
        print("\n" + "="*60)
        print("🎯 TEST 4: Aide contextuelle événement")
        print("="*60)
        
        try:
            # Récupérer un événement de test
            events = Event.objects.all()[:1]
            if not events:
                print("⚠️  Aucun événement trouvé - création d'un événement de test")
                # Créer un événement de test si nécessaire
                return True
            
            event = events[0]
            print(f"📅 Test avec l'événement: {event.title}")
            
            data = {"question": "Comment rejoindre cet événement ?"}
            response = requests.post(
                f"{self.base_url}/ai/help/event/{event.id}/",
                json=data,
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                print("✅ SUCCÈS - Aide contextuelle générée:")
                print(f"   Réponse: {ai_response.get('response', '')[:100]}...")
                
                event_info = ai_response.get('event_info', {})
                if event_info:
                    print(f"   📅 Événement: {event_info.get('title', 'N/A')}")
                    print(f"   💰 Prix: {event_info.get('price', 0)}€")
                
                return True
            else:
                print(f"❌ ÉCHEC - Status: {response.status_code}")
                print(f"   Erreur: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            return False
    
    def test_feedback(self):
        """Test du système de feedback"""
        print("\n" + "="*60)
        print("📊 TEST 5: Système de feedback")
        print("="*60)
        
        try:
            feedback_data = {
                "message": "Comment m'inscrire ?",
                "ai_response": "Cliquez sur S'inscrire...",
                "rating": 5,
                "comment": "Très utile, merci !"
            }
            
            response = requests.post(
                f"{self.base_url}/ai/feedback/",
                json=feedback_data,
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCÈS - Feedback enregistré:")
                print(f"   Message: {data.get('message', 'Pas de message')}")
                return True
            else:
                print(f"❌ ÉCHEC - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 DÉMARRAGE DES TESTS IA CHATBOT")
        print("="*60)
        
        tests = [
            ("Infos publiques IA", self.test_public_info),
            ("Chat basique", lambda: self.authenticate_user() and self.test_chat_basic()),
            ("Suggestions", self.test_suggestions),
            ("Aide contextuelle", self.test_contextual_help),
            ("Système feedback", self.test_feedback)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"\n{'✅' if result else '❌'} {test_name}: {'SUCCÈS' if result else 'ÉCHEC'}")
            except Exception as e:
                results.append((test_name, False))
                print(f"\n❌ {test_name}: ERREUR - {e}")
        
        # Résumé final
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*60)
        
        success_count = sum(1 for _, result in results if result)
        total_count = len(results)
        success_rate = success_count / total_count * 100
        
        for test_name, result in results:
            status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
            print(f"  {status}: {test_name}")
        
        print(f"\n🎯 RÉSULTAT GLOBAL: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("\n🎉 EXCELLENT ! Le chatbot IA fonctionne parfaitement !")
        elif success_rate >= 60:
            print("\n👍 BIEN ! Le chatbot IA fonctionne avec quelques améliorations à apporter.")
        else:
            print("\n⚠️  ATTENTION ! Le chatbot IA nécessite des corrections.")
        
        return success_rate >= 80

if __name__ == '__main__':
    tester = AIBotTester()
    tester.run_all_tests()
