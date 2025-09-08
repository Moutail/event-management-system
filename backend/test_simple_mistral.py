#!/usr/bin/env python
"""
Test ultra-simple de Mistral
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_simple():
    """Test ultra-simple"""
    print("🔍 Test ultra-simple de Mistral")
    print("=" * 40)
    
    # Vérifier la clé
    mistral_key = os.getenv('MISTRAL_API_KEY')
    if mistral_key:
        print(f"✅ Clé Mistral trouvée: {'*' * 20}...{mistral_key[-8:]}")
    else:
        print("❌ Clé Mistral non trouvée")
        return
    
    try:
        # Test d'import
        from mistralai.client import MistralClient
        print("✅ Import Mistral réussi")
        
        # Test de connexion
        client = MistralClient(api_key=mistral_key)
        print("✅ Client Mistral créé")
        
        # Test simple
        response = client.chat(
            model="mistral-tiny",
            messages=[{"role": "user", "content": "Dis-moi juste 'OK'"}]
        )
        
        print("✅ Connexion Mistral réussie !")
        print(f"   Réponse: {response.choices[0].message.content}")
        
        print("\n🎉 Mistral fonctionne parfaitement !")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    test_simple()

















