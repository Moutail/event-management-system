#!/usr/bin/env python
"""
Test rapide de Mistral dans le générateur IA
"""

import os
import sys
import django
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.ai_content_generator import get_ai_content_generator

def test_mistral_generator():
    """Test rapide de Mistral dans le générateur"""
    print("🤖 Test rapide de Mistral dans le générateur IA")
    print("=" * 60)
    
    try:
        # Récupérer le générateur IA
        print("🔍 Récupération du générateur IA...")
        generator = get_ai_content_generator()
        print("✅ Générateur IA récupéré avec succès")
        
        # Vérifier le modèle par défaut
        print(f"🎯 Modèle par défaut : {generator.default_model}")
        
        if generator.default_model == "none":
            print("❌ Aucun modèle IA disponible")
            return
        else:
            print(f"🎉 Modèle IA activé : {generator.default_model}")
        
        # Test rapide : Génération de description
        print("\n🔍 Test rapide : Génération de description...")
        
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
        
        # Test rapide : Génération de hashtags
        print("\n🔍 Test rapide : Génération de hashtags...")
        print("      🔄 Génération en cours...")
        
        hashtags = generator.generate_hashtags(
            title=test_event['title'],
            category=test_event['category']
        )
        
        print(f"      🏷️ Hashtags générés : {' '.join(hashtags)}")
        
        print("\n🎉 Test rapide réussi !")
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
    test_mistral_generator()













