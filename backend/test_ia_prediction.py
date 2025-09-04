#!/usr/bin/env python
"""
Test simple de l'IA de prédiction
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.predictive_analytics import get_predictive_service

def test_ia_prediction():
    """Test de l'IA de prédiction"""
    print("🧪 Test de l'IA de prédiction")
    print("=" * 40)
    
    try:
        # Récupérer le service
        print("🔍 Récupération du service prédictif...")
        predictive_service = get_predictive_service()
        print("✅ Service récupéré avec succès")
        
        # Tester les insights globaux
        print("\n🔍 Test des insights globaux...")
        insights = predictive_service.get_predictive_insights()
        print(f"✅ Insights récupérés: {len(insights.get('global_insights', []))} insights globaux")
        
        # Tester la détection des tendances
        print("\n🔍 Test de la détection des tendances...")
        trends = predictive_service.detect_emerging_trends(90)
        print(f"✅ Tendances détectées: {len(trends.get('emerging_trends', []))} tendances émergentes")
        print(f"✅ Catégories analysées: {len(trends.get('category_trends', []))} catégories")
        print(f"✅ Tags analysés: {len(trends.get('tag_trends', []))} tags")
        
        # Vérifier le statut des modèles
        print("\n🔍 Vérification des modèles ML...")
        model_path = os.path.join(os.getcwd(), 'ml_models', 'fill_rate_predictor.joblib')
        if os.path.exists(model_path):
            print("✅ Modèle de prédiction trouvé")
            model_age = os.path.getmtime(model_path)
            print(f"   Dernière modification: {model_age}")
        else:
            print("⚠️ Modèle de prédiction non trouvé")
            print("   Chemin recherché:", model_path)
        
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ia_prediction()














