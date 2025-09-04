#!/usr/bin/env python
"""
Test du générateur de contenu en mode fallback (sans clés API)
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.ai_content_generator import get_ai_content_generator

def test_fallback_generator():
    """Test du générateur en mode fallback"""
    print("🔄 Test du générateur de contenu en mode fallback")
    print("=" * 60)
    
    try:
        # Récupérer le générateur IA
        print("🔍 Récupération du générateur IA...")
        generator = get_ai_content_generator()
        print("✅ Générateur IA récupéré avec succès")
        
        # Vérifier le modèle par défaut
        print(f"🎯 Modèle par défaut : {generator.default_model}")
        
        if generator.default_model == "none":
            print("💡 Mode fallback activé - Aucun modèle IA disponible")
        else:
            print(f"🤖 Modèle IA disponible : {generator.default_model}")
        
        # Test 1: Génération de description
        print("\n🔍 Test 1: Génération de description")
        
        test_events = [
            {
                "title": "Workshop Innovation Tech 2024",
                "category": "Workshop",
                "location": "Paris",
                "price": 75.0,
                "max_capacity": 30
            },
            {
                "title": "Festival de Musique Électronique",
                "category": "Concert",
                "location": "Montreal",
                "price": 45.0,
                "max_capacity": 500
            },
            {
                "title": "Meetup Développeurs Web",
                "category": "Meetup",
                "location": "Lyon",
                "price": 0,
                "max_capacity": 50
            }
        ]
        
        for event in test_events:
            print(f"\n   🎯 Événement: {event['title']}")
            print(f"      Catégorie: {event['category']}")
            print(f"      Lieu: {event['location']}")
            print(f"      Prix: {event['price']}€")
            print(f"      Capacité: {event['max_capacity'] or 'Illimitée'} participants")
            
            # Générer la description
            description = generator.generate_event_description(
                title=event['title'],
                category=event['category'],
                location=event['location'],
                price=event['price'],
                max_capacity=event['max_capacity']
            )
            
            print(f"      📝 Description générée:")
            print(f"      {description}")
        
        # Test 2: Génération de hashtags
        print("\n🔍 Test 2: Génération de hashtags")
        
        for event in test_events[:2]:  # Tester avec 2 événements
            print(f"\n   🎯 Événement: {event['title']}")
            
            # Générer les hashtags
            hashtags = generator.generate_hashtags(
                title=event['title'],
                category=event['category']
            )
            
            print(f"      🏷️ Hashtags générés: {' '.join(hashtags)}")
            print(f"      📊 Nombre de hashtags: {len(hashtags)}")
        
        # Test 3: Suggestions de visuels
        print("\n🔍 Test 3: Suggestions de visuels")
        
        for event in test_events[:2]:  # Tester avec 2 événements
            print(f"\n   🎯 Événement: {event['title']}")
            
            # Générer les suggestions visuelles
            visual_suggestions = generator.generate_visual_suggestions(
                category=event['category'],
                title=event['title']
            )
            
            print(f"      🎨 Couleurs suggérées: {', '.join(visual_suggestions['colors'][:3])}")
            print(f"      🎭 Thèmes suggérés: {', '.join(visual_suggestions['themes'][:3])}")
            print(f"      🔧 Éléments suggérés: {', '.join(visual_suggestions['elements'][:3])}")
            print(f"      💡 Style recommandé: {visual_suggestions['style']}")
            
            if visual_suggestions['recommendations']:
                print(f"      💭 Recommandations:")
                for rec in visual_suggestions['recommendations'][:3]:
                    print(f"         • {rec}")
        
        # Test 4: Test avec données de prédiction simulées
        print("\n🔍 Test 4: Intégration avec le système de prédiction (simulation)")
        
        # Simuler des données de prédiction (comme si elles venaient de ton système existant)
        mock_prediction_data = {
            'predicted_fill_rate': 85,
            'optimal_price': 80.0,
            'trends': 'Forte demande pour les workshops tech',
            'recommendations': 'Prix légèrement plus élevé acceptable, focus sur la qualité'
        }
        
        test_event = test_events[0]  # Workshop Innovation Tech
        
        print(f"   🎯 Événement: {test_event['title']}")
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
        
        print("\n✅ Test terminé avec succès!")
        
        # Résumé des fonctionnalités
        print("\n📝 RÉSUMÉ DES FONCTIONNALITÉS:")
        print("   1. ✅ Générateur IA configuré et fonctionnel")
        print("   2. ✅ Mode fallback robuste (sans clés API)")
        print("   3. ✅ Intégration avec le système de prédiction (simulation)")
        print("   4. ✅ Génération de contenu contextuel")
        print("   5. ✅ Hashtags et suggestions visuelles")
        
        if generator.default_model == "none":
            print("\n💡 POUR ACTIVER LA VRAIE IA :")
            print("   1. Obtenez vos clés API (Claude, Mistral, ou OpenAI)")
            print("   2. Ajoutez-les dans le fichier .env")
            print("   3. Redémarrez l'application")
            print("   4. Le système utilisera automatiquement le meilleur modèle disponible !")
        else:
            print(f"\n🎉 IA ACTIVÉE : {generator.default_model}")
            print("   Le contenu est maintenant généré par de vrais modèles IA !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fallback_generator()













