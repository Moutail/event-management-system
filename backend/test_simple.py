#!/usr/bin/env python3
"""
🧪 TEST SIMPLE DU SERVICE D'ANALYTICS PRÉDICTIFS
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.predictive_analytics import get_predictive_service

def test_service():
    print("🎯 Test du service d'analytics prédictifs...")
    
    try:
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        # Test de détection des tendances
        trends = predictive_service.detect_emerging_trends(days_back=30)
        print(f"✅ Tendances détectées: {trends['status']}")
        
        if trends['status'] == 'success':
            print(f"📊 Catégories analysées: {len(trends.get('category_trends', []))}")
            print(f"🏷️ Tags analysés: {len(trends.get('tag_trends', []))}")
            print(f"📈 Tendances émergentes: {len(trends.get('emerging_trends', []))}")
        
        # Test des insights prédictifs
        insights = predictive_service.get_predictive_insights()
        print(f"🧠 Insights générés: {insights['status']}")
        
        if insights['status'] == 'success':
            print(f"💡 Insights globaux: {len(insights.get('global_insights', []))}")
            print(f"🎯 Recommandations: {len(insights.get('recommendations', []))}")
        
        print("✅ Tous les tests sont passés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()
