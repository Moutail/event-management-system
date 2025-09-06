#!/usr/bin/env python
"""
Test du nouveau générateur de contenu IA
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.ai_content_generator import get_ai_content_generator
from ai_config import check_ai_availability

def test_ai_generator():
    """Test du générateur de contenu IA"""
    print("🤖 Test du nouveau générateur de contenu IA")
    print("=" * 60)
    
    # Vérifier la configuration IA
    print("🔍 Vérification de la configuration IA...")
    ai_status = check_ai_availability()
    
    if not ai_status['available']:
        print("❌ Aucun modèle IA configuré")
        print("💡 Pour tester, configurez une clé API dans votre fichier .env")
        print("   Exemple : ANTHROPIC_API_KEY=votre_clé_ici")
        return
    
    print(f"✅ {ai_status['total_models']} modèle(s) IA disponible(s)")
    print(f"🎯 Modèle par défaut : {ai_status['default_model']}")
    
    try:
        # Récupérer le générateur IA
        print("\n🔍 Récupération du générateur IA...")
        generator = get_ai_content_generator()
        print("✅ Générateur IA récupéré avec succès")
        
        # Test 1: Génération de description avec IA
        print("\n🔍 Test 1: Génération de description avec IA")
        
        test_event = {
            "title": "Workshop Innovation Tech 2024",
            "category": "Workshop",
            "location": "Paris",
            "price": 75.0,
            "max_capacity": 30
        }
        
        print(f"   🎯 Événement: {test_event['title']}")
        print(f"      Catégorie: {test_event['category']}")
        print(f"      Lieu: {test_event['location']}")
        print(f"      Prix: {test_event['price']}€")
        print(f"      Capacité: {test_event['max_capacity']} participants")
        
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
        
        # Test 2: Génération de hashtags avec IA
        print("\n🔍 Test 2: Génération de hashtags avec IA")
        
        hashtags = generator.generate_hashtags(
            title=test_event['title'],
            category=test_event['category'],
            description=description
        )
        
        print(f"      🏷️ Hashtags générés par l'IA:")
        print(f"      {' '.join(hashtags)}")
        print(f"      📊 Nombre de hashtags: {len(hashtags)}")
        
        # Test 3: Suggestions visuelles avec IA
        print("\n🔍 Test 3: Suggestions visuelles avec IA")
        
        visual_suggestions = generator.generate_visual_suggestions(
            category=test_event['category'],
            title=test_event['title'],
            description=description
        )
        
        print(f"      🎨 Couleurs suggérées: {', '.join(visual_suggestions['colors'][:3])}")
        print(f"      🎭 Thèmes suggérés: {', '.join(visual_suggestions['themes'][:3])}")
        print(f"      🔧 Éléments suggérés: {', '.join(visual_suggestions['elements'][:3])}")
        print(f"      💡 Style recommandé: {visual_suggestions['style']}")
        
        if visual_suggestions['recommendations']:
            print(f"      💭 Recommandations:")
            for rec in visual_suggestions['recommendations'][:3]:
                print(f"         • {rec}")
        
        # Test 4: Test avec données de prédiction (simulation)
        print("\n🔍 Test 4: Intégration avec le système de prédiction (simulation)")
        
        # Simuler des données de prédiction (comme si elles venaient de ton système existant)
        mock_prediction_data = {
            'predicted_fill_rate': 85,
            'optimal_price': 80.0,
            'trends': 'Forte demande pour les workshops tech',
            'recommendations': 'Prix légèrement plus élevé acceptable, focus sur la qualité'
        }
        
        print(f"      🚀 Données de prédiction simulées:")
        print(f"         - Taux de remplissage prévu: {mock_prediction_data['predicted_fill_rate']}%")
        print(f"         - Prix optimal: {mock_prediction_data['optimal_price']}€")
        print(f"         - Tendances: {mock_prediction_data['trends']}")
        
        # Générer du contenu optimisé avec les données de prédiction
        optimized_description = generator.generate_event_description(
            title=test_event['title'],
            category=test_event['category'],
            location=test_event['location'],
            price=test_event['price'],
            max_capacity=test_event['max_capacity'],
            prediction_data=mock_prediction_data
        )
        
        print(f"      📝 Description optimisée avec l'IA de prédiction:")
        print(f"      {optimized_description}")
        
        # Test 5: Test de fallback (sans IA)
        print("\n🔍 Test 5: Test de fallback (sans IA)")
        
        # Simuler un générateur sans IA
        fallback_description = generator._generate_fallback_description(
            title=test_event['title'],
            category=test_event['category'],
            location=test_event['location'],
            price=test_event['price'],
            max_capacity=test_event['max_capacity']
        )
        
        print(f"      📝 Description de fallback:")
        print(f"      {fallback_description}")
        
        print("\n✅ Test terminé avec succès!")
        
        # Résumé des fonctionnalités
        print("\n📝 RÉSUMÉ DES NOUVELLES FONCTIONNALITÉS:")
        print("   1. ✅ Vraie IA (Claude/Mistral/OpenAI) au lieu de templates")
        print("   2. ✅ Intégration avec ton système de prédiction existant")
        print("   3. ✅ Génération de contenu contextuel et optimisé")
        print("   4. ✅ Hashtags intelligents et personnalisés")
        print("   5. ✅ Suggestions visuelles adaptatives")
        print("   6. ✅ Système de fallback robuste")
        
        print(f"\n🎯 Modèle IA utilisé: {ai_status['default_model']}")
        print("💡 Le contenu généré est maintenant vraiment intelligent et unique !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ai_generator()
















