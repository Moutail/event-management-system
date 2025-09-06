#!/usr/bin/env python
"""
Test correct pour Mistral AI version 1.9.7
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_mistral_correct():
    """Test avec la bonne structure Mistral"""
    print("🔍 Test correct de Mistral AI v1.9.7")
    print("=" * 50)
    
    try:
        # Test 1: Import de base
        print("📦 Test 1: Import de base...")
        from mistralai.client import MistralClient
        print("✅ MistralClient importé")
        
        # Test 2: Vérification de la clé API
        print("\n🔑 Test 2: Vérification de la clé API...")
        mistral_key = os.getenv('MISTRAL_API_KEY')
        if mistral_key:
            print(f"✅ Clé Mistral trouvée: {'*' * 20}...{mistral_key[-8:]}")
        else:
            print("❌ Clé Mistral non trouvée")
            return
        
        # Test 3: Création du client
        print("\n🤖 Test 3: Création du client Mistral...")
        try:
            client = MistralClient(api_key=mistral_key)
            print("✅ Client Mistral créé avec succès")
        except Exception as e:
            print(f"❌ Erreur création client: {str(e)}")
            return
        
        # Test 4: Test de connexion simple
        print("\n🔌 Test 4: Test de connexion...")
        try:
            # Test simple avec un message court
            response = client.chat(
                model="mistral-tiny",
                messages=[{"role": "user", "content": "Dis-moi juste 'OK'"}]
            )
            print("✅ Connexion Mistral réussie !")
            print(f"   Réponse: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ Erreur connexion: {str(e)}")
            return
        
        print("\n🎉 TOUS LES TESTS MISTRAL SONT RÉUSSIS !")
        print("💡 Mistral AI est prêt à être utilisé !")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {str(e)}")
        print("💡 Vérifiez que mistralai est installé: pip install mistralai")
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")

if __name__ == "__main__":
    test_mistral_correct()
















