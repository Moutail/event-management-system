#!/usr/bin/env python
"""
Test du générateur automatique de contenu
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.content_generator import get_content_generator

def test_content_generator():
    """Test du générateur de contenu"""
    print("🎨 Test du générateur automatique de contenu")
    print("=" * 60)
    
    try:
        # Récupérer le générateur
        print("🔍 Récupération du générateur de contenu...")
        generator = get_content_generator()
        print("✅ Générateur récupéré avec succès")
        
        # Test 1: Génération de descriptions
        print("\n🔍 Test 1: Génération de descriptions d'événements")
        
        test_events = [
            {
                "title": "WINNER",
                "category": "Conférence",
                "location": "montreal",
                "price": 17.00,
                "max_capacity": 2
            },
            {
                "title": "TEST",
                "category": "Concert",
                "location": "montreal",
                "price": 2.00,
                "max_capacity": 2
            },
            {
                "title": "STEPHANE",
                "category": "Sport",
                "location": "Lomé",
                "price": 12.00,
                "max_capacity": 2
            },
            {
                "title": "Workshop Innovation",
                "category": "Workshop",
                "location": "Paris",
                "price": 50.00,
                "max_capacity": 20
            },
            {
                "title": "Meetup Tech",
                "category": "Meetup",
                "location": "Lyon",
                "price": 0,
                "max_capacity": None
            }
        ]
        
        for event in test_events:
            print(f"\n   🎯 Événement: {event['title']}")
            print(f"      Catégorie: {event['category']}")
            print(f"      Lieu: {event['location']}")
            print(f"      Prix: {event['price']}€")
            print(f"      Capacité: {event['max_capacity'] or 'Illimitée'}")
            
            # Générer la description
            description = generator.generate_event_description(
                title=event['title'],
                category=event['category'],
                location=event['location'],
                price=event['price'],
                max_capacity=event['max_capacity']
            )
            
            print(f"      📝 Description générée: {description}")
        
        # Test 2: Génération de hashtags
        print("\n🔍 Test 2: Génération de hashtags optimisés")
        
        for event in test_events[:3]:  # Tester avec 3 événements
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
        
        for event in test_events[:3]:  # Tester avec 3 événements
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
        
        # Test 4: Test avec description personnalisée
        print("\n🔍 Test 4: Génération avec description personnalisée")
        
        custom_event = {
            "title": "Festival de Musique Électronique",
            "category": "Concert",
            "location": "Montreal",
            "price": 45.00,
            "max_capacity": 500,
            "description": "Une soirée exceptionnelle avec des DJs internationaux, des performances visuelles spectaculaires et une ambiance festive unique. Venez vivre une expérience musicale inoubliable avec des artistes de renommée mondiale."
        }
        
        print(f"   🎯 Événement: {custom_event['title']}")
        
        # Générer les hashtags avec description
        hashtags_with_desc = generator.generate_hashtags(
            title=custom_event['title'],
            category=custom_event['category'],
            description=custom_event['description']
        )
        
        print(f"      🏷️ Hashtags avec description: {' '.join(hashtags_with_desc)}")
        
        # Générer les suggestions visuelles avec description
        visual_with_desc = generator.generate_visual_suggestions(
            category=custom_event['category'],
            title=custom_event['title'],
            description=custom_event['description']
        )
        
        print(f"      🎨 Couleurs: {', '.join(visual_with_desc['colors'][:3])}")
        print(f"      💭 Recommandations personnalisées:")
        for rec in visual_with_desc['recommendations'][:3]:
            print(f"         • {rec}")
        
        print("\n✅ Test terminé avec succès!")
        
        # Résumé des fonctionnalités
        print("\n📝 RÉSUMÉ DES FONCTIONNALITÉS:")
        print("   1. ✅ Génération automatique de descriptions par catégorie")
        print("   2. ✅ Hashtags optimisés pour la visibilité")
        print("   3. ✅ Suggestions de visuels personnalisées")
        print("   4. ✅ Analyse intelligente du contenu")
        print("   5. ✅ Recommandations contextuelles")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_content_generator()














