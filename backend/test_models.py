#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC DES DONNÉES DE CATÉGORIES - APRÈS CORRECTION
"""

import os
import sys
import django
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, Category, EventRegistration
from django.utils import timezone
from django.db.models import Count, Q

def debug_category_data():
    print("🔍 DIAGNOSTIC DES DONNÉES DE CATÉGORIES - APRÈS CORRECTION")
    print("=" * 70)
    
    # Période d'analyse (90 jours)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"📅 Période analysée: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    print()
    
    # 1. Vérifier le nombre total d'événements
    total_events = Event.objects.count()
    print(f"📊 TOTAL ÉVÉNEMENTS DANS LA BASE: {total_events}")
    
    # 2. Vérifier les événements par statut
    events_by_status = Event.objects.values('status').annotate(count=Count('id'))
    print("\n📋 Événements par statut:")
    for item in events_by_status:
        print(f"   • {item['status']}: {item['count']}")
    
    # 3. Vérifier les événements créés dans la période
    recent_events = Event.objects.filter(created_at__gte=start_date).count()
    print(f"\n📅 Événements créés dans les 90 derniers jours: {recent_events}")
    
    # 4. Analyser chaque catégorie individuellement
    print("\n🏷️ ANALYSE PAR CATÉGORIE:")
    print("-" * 40)
    
    categories = Category.objects.all()
    for category in categories:
        print(f"\n📂 Catégorie: {category.name}")
        
        # Compter les événements de cette catégorie (AVEC distinct=True)
        total_in_category = Event.objects.filter(category=category).count()
        recent_in_category = Event.objects.filter(
            category=category,
            created_at__gte=start_date
        ).count()
        
        print(f"   • Total dans la catégorie: {total_in_category}")
        print(f"   • Créés récemment (90j): {recent_in_category}")
        
        # Vérifier les événements uniques
        events_in_category = Event.objects.filter(category=category).values_list('id', 'title', 'created_at')[:5]
        print(f"   • Événements (ID, Titre, Date création):")
        for event_id, title, created_at in events_in_category:
            print(f"     - {event_id}: {title} ({created_at.strftime('%Y-%m-%d')})")
        
        if total_in_category > 5:
            print(f"     ... et {total_in_category - 5} autres")
    
    # 5. Test du service corrigé
    print("\n🧪 TEST DU SERVICE CORRIGÉ:")
    print("-" * 40)
    
    try:
        from events.predictive_analytics import get_predictive_service
        service = get_predictive_service()
        
        print("✅ Service récupéré avec succès")
        
        # Tester la détection des tendances
        print("🔍 Test de detect_emerging_trends...")
        trends = service.detect_emerging_trends(days_back=90)
        
        if trends['status'] == 'success':
            print("✅ Tendances détectées avec succès")
            print(f"📊 Catégories analysées: {len(trends['category_trends'])}")
            
            for cat in trends['category_trends']:
                print(f"   • {cat['name']}: {cat['recent_events']} récents / {cat['total_events']} total")
        else:
            print(f"❌ Erreur: {trends.get('message', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test du service: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 6. Résumé
    print("\n📊 RÉSUMÉ:")
    print("-" * 40)
    print(f"   • Total événements: {total_events}")
    print(f"   • Événements récents (90j): {recent_events}")
    print(f"   • Différence: {total_events - recent_events} événements anciens")
    
    if total_events != recent_events:
        print("ℹ️  Normal: Il y a des événements créés il y a plus de 90 jours")
    
    print("\n🎯 VÉRIFICATION:")
    if total_events <= 100:
        print("✅ Les données semblent cohérentes (moins de 100 événements)")
    else:
        print("⚠️  ATTENTION: Nombre d'événements suspect (>100)")

if __name__ == "__main__":
    debug_category_data()
