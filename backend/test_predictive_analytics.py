#!/usr/bin/env python3
"""
🧪 TEST DES ANALYTICS PRÉDICTIFS
Script de test pour vérifier le fonctionnement des fonctionnalités d'IA
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.predictive_analytics import predictive_service
from events.models import Event, User, Category, Tag, EventRegistration
from django.utils import timezone

def test_predictive_service():
    """Test du service d'analytics prédictifs"""
    print("🎯 TEST DU SERVICE D'ANALYTICS PRÉDICTIFS")
    print("=" * 50)
    
    try:
        # Test 1: Vérification de l'initialisation
        print("\n1️⃣ Test d'initialisation...")
        print(f"   Répertoire des modèles: {predictive_service.models_dir}")
        print(f"   Répertoire existe: {os.path.exists(predictive_service.models_dir)}")
        
        # Test 2: Entraînement du modèle
        print("\n2️⃣ Test d'entraînement du modèle...")
        training_result = predictive_service.train_fill_rate_predictor()
        print(f"   Résultat: {training_result['status']}")
        if training_result['status'] == 'success':
            print(f"   Métriques: {training_result['metrics']}")
        elif training_result['status'] == 'insufficient_data':
            print(f"   Message: {training_result['message']}")
        
        # Test 3: Détection des tendances
        print("\n3️⃣ Test de détection des tendances...")
        trends = predictive_service.detect_emerging_trends(days_back=30)
        print(f"   Statut: {trends['status']}")
        if trends['status'] == 'success':
            print(f"   Tendances émergentes: {len(trends['emerging_trends'])}")
            print(f"   Catégories analysées: {len(trends['category_trends'])}")
            print(f"   Tags analysés: {len(trends['tag_trends'])}")
        
        # Test 4: Insights prédictifs
        print("\n4️⃣ Test des insights prédictifs...")
        insights = predictive_service.get_predictive_insights()
        print(f"   Statut: {insights['status']}")
        if insights['status'] == 'success':
            print(f"   Insights globaux: {len(insights['global_insights'])}")
            print(f"   Recommandations: {len(insights['recommendations'])}")
        
        # Test 5: Analyse d'un événement spécifique (si disponible)
        print("\n5️⃣ Test d'analyse d'événement spécifique...")
        events = Event.objects.filter(status='published')[:1]
        if events:
            event = events[0]
            print(f"   Événement testé: {event.title}")
            
            # Prédiction de remplissage
            event_data = {
                'id': event.id,
                'price': float(event.price),
                'max_capacity': event.max_capacity or 100,
                'category': event.category.name if event.category else '',
                'city': event.location.split(',')[0] if event.location else '',
                'country': event.location.split(',')[-1].strip() if event.location else '',
                'start_date': event.start_date,
                'duration_hours': 2,
                'organizer_events_count': event.organizer.events_organized.count() if event.organizer else 0,
                'organizer_avg_rating': getattr(event.organizer.profile, 'rating', 0) if event.organizer and hasattr(event.organizer, 'profile') else 0,
                'tags_count': event.tags.count()
            }
            
            prediction = predictive_service.predict_event_fill_rate(event_data)
            print(f"   Prédiction: {prediction['status']}")
            if prediction['status'] == 'success':
                print(f"   Taux prédit: {prediction['prediction']*100:.1f}%")
                print(f"   Confiance: {prediction['confidence']*100:.1f}%")
            
            # Optimisation des prix
            optimization = predictive_service.optimize_event_pricing(event_data)
            print(f"   Optimisation: {optimization['status']}")
            if optimization['status'] == 'success':
                print(f"   Prix optimal: {optimization['optimal_price']}€")
                print(f"   Changement: {optimization['price_change_percent']}%")
        
        print("\n✅ Tests terminés avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()

def test_data_availability():
    """Vérifie la disponibilité des données pour l'entraînement"""
    print("\n📊 VÉRIFICATION DE LA DISPONIBILITÉ DES DONNÉES")
    print("=" * 50)
    
    try:
        # Statistiques générales
        total_events = Event.objects.count()
        published_events = Event.objects.filter(status='published').count()
        past_events = Event.objects.filter(start_date__lt=timezone.now()).count()
        total_users = User.objects.count()
        total_registrations = EventRegistration.objects.count()
        
        print(f"   Total événements: {total_events}")
        print(f"   Événements publiés: {published_events}")
        print(f"   Événements passés: {past_events}")
        print(f"   Total utilisateurs: {total_users}")
        print(f"   Total inscriptions: {total_registrations}")
        
        # Vérification des catégories et tags
        categories = Category.objects.count()
        tags = Tag.objects.count()
        print(f"   Catégories: {categories}")
        print(f"   Tags: {tags}")
        
        # Vérification des données temporelles
        if past_events > 0:
            oldest_event = Event.objects.filter(start_date__lt=timezone.now()).order_by('start_date').first()
            newest_event = Event.objects.filter(start_date__lt=timezone.now()).order_by('start_date').last()
            
            if oldest_event and newest_event:
                date_range = newest_event.start_date - oldest_event.start_date
                print(f"   Plage temporelle: {date_range.days} jours")
        
        # Recommandations
        if past_events < 50:
            print(f"\n⚠️  ATTENTION: Seulement {past_events} événements passés disponibles")
            print("   Pour un bon entraînement, il est recommandé d'avoir au moins 50 événements")
        
        if total_registrations < 100:
            print(f"\n⚠️  ATTENTION: Seulement {total_registrations} inscriptions disponibles")
            print("   Pour un bon entraînement, il est recommandé d'avoir au moins 100 inscriptions")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la vérification des données: {str(e)}")

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS DES ANALYTICS PRÉDICTIFS")
    print("=" * 60)
    
    # Vérification des données
    test_data_availability()
    
    # Tests du service
    test_predictive_service()
    
    print("\n🎉 TOUS LES TESTS SONT TERMINÉS!")
    print("=" * 60)

if __name__ == "__main__":
    main()
