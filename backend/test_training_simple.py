#!/usr/bin/env python3
"""
🧪 TEST SIMPLE D'ENTRAÎNEMENT DES MODÈLES ML
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.predictive_analytics import get_predictive_service

def test_training():
    print("🎯 Test d'entraînement des modèles ML...")
    
    try:
        # Récupérer le service
        service = get_predictive_service()
        print("✅ Service récupéré avec succès")
        
        # Tester l'entraînement
        print("🚀 Début de l'entraînement...")
        result = service.train_fill_rate_predictor()
        
        print(f"📊 Résultat: {result['status']}")
        print(f"💬 Message: {result['message']}")
        
        if result['status'] == 'success':
            print("✅ Modèle entraîné avec succès!")
            if 'metrics' in result:
                print(f"📈 Métriques: {result['metrics']}")
        elif result['status'] == 'insufficient_data':
            print(f"⚠️ Données insuffisantes: {result['message']}")
        elif result['status'] == 'up_to_date':
            print(f"ℹ️ Modèle déjà à jour: {result['message']}")
        else:
            print(f"❌ Erreur: {result['message']}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training()

















