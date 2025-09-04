#!/usr/bin/env python3
"""
🧪 TEST D'ENTRAÎNEMENT DU MODÈLE ML
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.predictive_analytics import predictive_service

def test_training():
    print("🎯 Test d'entraînement du modèle ML...")
    
    try:
        # Test d'entraînement du modèle
        result = predictive_service.train_fill_rate_predictor()
        print(f"Résultat: {result['status']}")
        print(f"Message: {result['message']}")
        
        if result['status'] == 'success':
            print(f"✅ Modèle entraîné avec succès!")
            print(f"📊 Métriques: {result.get('metrics', {})}")
        elif result['status'] == 'insufficient_data':
            print(f"⚠️ Données insuffisantes: {result['message']}")
        elif result['status'] == 'up_to_date':
            print(f"ℹ️ Modèle déjà à jour: {result['message']}")
        else:
            print(f"❌ Erreur: {result['message']}")
        
        # Test de prédiction (si le modèle est disponible)
        if result['status'] in ['success', 'up_to_date']:
            print("\n🔮 Test de prédiction...")
            
            # Créer des données d'événement de test
            test_event_data = {
                'price': 50.0,
                'max_capacity': 100,
                'duration_hours': 2,
                'organizer_events_count': 5,
                'organizer_avg_rating': 4.5,
                'days_until_event': 30,
                'category_popularity': 10,
                'tags_count': 3,
                'start_date': '2024-06-15T14:00:00Z',
                'city': 'Paris',
                'country': 'France',
                'category': 'Conférence',
                'avg_price_similar_events': 45.0
            }
            
            prediction = predictive_service.predict_event_fill_rate(test_event_data)
            print(f"Prédiction: {prediction['status']}")
            
            if prediction['status'] == 'success':
                print(f"🎯 Taux de remplissage prédit: {prediction['prediction']*100:.1f}%")
                print(f"📊 Confiance: {prediction['confidence']*100:.1f}%")
                print(f"👥 Inscriptions prédites: {prediction['predicted_registrations']}")
        
        print("\n✅ Test d'entraînement terminé!")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training()















