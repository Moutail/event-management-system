#!/usr/bin/env python3
"""
🧪 TEST DES ANALYTICS SPÉCIFIQUES À UN ÉVÉNEMENT
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event
from events.predictive_analytics import get_predictive_service

def test_event_specific_analytics():
    print("🎯 Test des analytics spécifiques à un événement...")
    
    try:
        # Récupérer le service
        service = get_predictive_service()
        print("✅ Service récupéré avec succès")
        
        # Récupérer un événement de test
        event = Event.objects.filter(status='published').first()
        if not event:
            print("❌ Aucun événement publié trouvé")
            return
        
        print(f"🎯 Test sur l'événement: {event.title} (ID: {event.id})")
        
        # Tester les analytics spécifiques à l'événement
        print("🚀 Test des analytics spécifiques...")
        insights = service.get_predictive_insights(event_id=event.id)
        
        print(f"📊 Résultat: {insights['status']}")
        if insights['status'] == 'success':
            print("✅ Analytics générés avec succès!")
            print(f"📈 Insights globaux: {len(insights.get('global_insights', []))}")
            print(f"🎯 Insights spécifiques: {len(insights.get('event_specific_insights', []))}")
            print(f"💡 Recommandations: {len(insights.get('recommendations', []))}")
            
            if insights.get('event_specific_insights'):
                print("\n🔍 Insights spécifiques à l'événement:")
                for insight in insights['event_specific_insights']:
                    print(f"   • {insight}")
        else:
            print(f"❌ Erreur: {insights.get('message', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_event_specific_analytics()


















