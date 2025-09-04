#!/usr/bin/env python
"""
Test direct du générateur IA avec Mistral
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_direct():
    """Test direct du générateur IA"""
    print("🤖 Test direct du générateur IA avec Mistral")
    print("=" * 60)
    
    try:
        # Test d'import direct
        print("📦 Test d'import...")
        from events.ai_content_generator import AIContentGenerator
        print("✅ Import réussi")
        
        # Créer le générateur
        print("\n🔍 Création du générateur...")
        generator = AIContentGenerator()
        print("✅ Générateur créé")
        
        # Vérifier le modèle par défaut
        print(f"🎯 Modèle par défaut : {generator.default_model}")
        
        if generator.default_model == "none":
            print("❌ Aucun modèle IA disponible")
            return
        else:
            print(f"🎉 Modèle IA activé : {generator.default_model}")
        
        # Test de génération
        print("\n🔍 Test de génération...")
        
        test_event = {
            "title": "Workshop Innovation Tech 2024",
            "category": "Workshop",
            "location": "Paris",
            "price": 75.0,
            "max_capacity": 30
        }
        
        print(f"   🎯 Événement: {test_event['title']}")
        print("      🔄 Génération en cours...")
        
        # Générer la description
        description = generator.generate_event_description(
            title=test_event['title'],
            category=test_event['category'],
            location=test_event['location'],
            price=test_event['price'],
            max_capacity=test_event['max_capacity']
        )
        
        print(f"      📝 Description générée par l'IA:")
        print(f"      {description}")
        
        # Test de hashtags
        print("\n🔍 Test de hashtags...")
        print("      🔄 Génération en cours...")
        
        hashtags = generator.generate_hashtags(
            title=test_event['title'],
            category=test_event['category']
        )
        
        print(f"      🏷️ Hashtags générés : {' '.join(hashtags)}")
        
        print("\n🎉 Test réussi !")
        print(f"🎯 Modèle utilisé : {generator.default_model}")
        
        if generator.default_model == "mistral":
            print("✅ Mistral AI fonctionne parfaitement dans le générateur !")
        else:
            print(f"⚠️ Modèle utilisé : {generator.default_model}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ai_direct()













