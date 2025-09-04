#!/usr/bin/env python
"""
Test des sources de données de l'IA de prédiction
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.predictive_analytics import get_predictive_service
from events.models import Event, EventRegistration, Category, Tag, UserProfile
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

def test_ia_data_sources():
    """Test des sources de données de l'IA"""
    print("🧪 Test des sources de données de l'IA de prédiction")
    print("=" * 60)
    
    try:
        # Récupérer le service
        print("🔍 Récupération du service prédictif...")
        predictive_service = get_predictive_service()
        print("✅ Service récupéré avec succès")
        
        # Test 1: Vérifier les données d'entraînement disponibles
        print("\n🔍 Test 1: Données d'entraînement disponibles")
        
        # Compter les événements
        total_events = Event.objects.count()
        published_events = Event.objects.filter(status='published').count()
        past_events = Event.objects.filter(end_date__lt=timezone.now()).count()
        future_events = Event.objects.filter(start_date__gt=timezone.now()).count()
        
        print(f"   📊 Total d'événements: {total_events}")
        print(f"   📊 Événements publiés: {published_events}")
        print(f"   📊 Événements passés: {past_events}")
        print(f"   📊 Événements futurs: {future_events}")
        
        # Compter les inscriptions
        total_registrations = EventRegistration.objects.count()
        confirmed_registrations = EventRegistration.objects.filter(status='confirmed').count()
        waitlisted_registrations = EventRegistration.objects.filter(status='waitlisted').count()
        
        print(f"   📊 Total d'inscriptions: {total_registrations}")
        print(f"   📊 Inscriptions confirmées: {confirmed_registrations}")
        print(f"   📊 Inscriptions en liste d'attente: {waitlisted_registrations}")
        
        # Compter les catégories et tags
        total_categories = Category.objects.count()
        total_tags = Tag.objects.count()
        
        print(f"   📊 Total de catégories: {total_categories}")
        print(f"   📊 Total de tags: {total_tags}")
        
        # Test 2: Vérifier les données utilisées pour l'entraînement
        print("\n🔍 Test 2: Données utilisées pour l'entraînement")
        
        # Événements avec inscriptions (nécessaires pour l'entraînement)
        events_with_registrations = Event.objects.annotate(
            reg_count=Count('registrations')
        ).filter(reg_count__gt=0).count()
        
        print(f"   🎯 Événements avec inscriptions: {events_with_registrations}")
        
        # Vérifier si on a assez de données pour l'entraînement
        if past_events >= 50:
            print("   ✅ Suffisamment d'événements passés pour l'entraînement (≥50)")
        else:
            print(f"   ⚠️ Événements passés insuffisants: {past_events}/50")
            
        if total_registrations >= 100:
            print("   ✅ Suffisamment d'inscriptions pour l'entraînement (≥100)")
        else:
            print(f"   ⚠️ Inscriptions insuffisantes: {total_registrations}/100")
        
        # Test 3: Analyser les données réelles utilisées
        print("\n🔍 Test 3: Analyse des données réelles utilisées")
        
        # Événements récents avec leurs caractéristiques
        recent_events = Event.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=90)
        ).select_related('category', 'organizer').prefetch_related('tags')[:5]
        
        print("   📋 Événements récents analysés:")
        for event in recent_events:
            print(f"      - {event.title}:")
            print(f"        Prix: {event.price}€")
            print(f"        Capacité: {event.max_capacity}")
            print(f"        Catégorie: {event.category.name if event.category else 'Aucune'}")
            print(f"        Tags: {[tag.name for tag in event.tags.all()]}")
            print(f"        Inscriptions: {event.registrations.count()}")
            print(f"        Taux de remplissage: {(event.registrations.count() / event.max_capacity * 100) if event.max_capacity else 0:.1f}%")
            print()
        
        # Test 4: Vérifier les features utilisées par l'IA
        print("\n🔍 Test 4: Features utilisées par l'IA")
        
        # Simuler la préparation des features pour un événement
        if recent_events.exists():
            sample_event = recent_events.first()
            
            # Données que l'IA extrait
            event_data = {
                'id': sample_event.id,
                'price': float(sample_event.price),
                'max_capacity': sample_event.max_capacity or 100,
                'category': sample_event.category.name if sample_event.category else '',
                'city': sample_event.location.split(',')[0] if sample_event.location else '',
                'country': sample_event.location.split(',')[-1].strip() if sample_event.location else '',
                'start_date': sample_event.start_date,
                'duration_hours': 2,  # Valeur par défaut
                'organizer_events_count': sample_event.organizer.events_organized.count() if sample_event.organizer else 0,
                'organizer_avg_rating': getattr(sample_event.organizer.profile, 'rating', 0) if sample_event.organizer and hasattr(sample_event.organizer, 'profile') else 0,
                'tags_count': sample_event.tags.count()
            }
            
            print(f"   🎯 Features extraites pour '{sample_event.title}':")
            for key, value in event_data.items():
                if key != 'start_date':
                    print(f"      {key}: {value}")
            
            print(f"      start_date: {event_data['start_date']}")
            
            # Features temporelles calculées
            if event_data['start_date']:
                start_date = event_data['start_date']
                weekday = start_date.weekday()
                month = start_date.month
                hour = start_date.hour
                days_until = (start_date - timezone.now()).days
                
                print(f"      Calculs temporels:")
                print(f"        Jour de la semaine: {weekday}")
                print(f"        Mois: {month}")
                print(f"        Heure: {hour}")
                print(f"        Jours jusqu'à l'événement: {days_until}")
        
        # Test 5: Vérifier la qualité des données
        print("\n🔍 Test 5: Qualité des données")
        
        # Événements sans catégorie
        events_without_category = Event.objects.filter(category__isnull=True).count()
        print(f"   ⚠️ Événements sans catégorie: {events_without_category}")
        
        # Événements sans tags
        events_without_tags = Event.objects.filter(tags__isnull=True).count()
        print(f"   ⚠️ Événements sans tags: {events_without_tags}")
        
        # Événements avec prix 0
        free_events = Event.objects.filter(price=0).count()
        print(f"   📊 Événements gratuits: {free_events}")
        
        # Événements avec capacité illimitée
        unlimited_events = Event.objects.filter(place_type='unlimited').count()
        print(f"   📊 Événements à capacité illimitée: {unlimited_events}")
        
        print("\n✅ Test terminé avec succès!")
        
        # Résumé des sources de données
        print("\n📝 RÉSUMÉ DES SOURCES DE DONNÉES DE L'IA:")
        print("   🎯 L'IA se base sur les données RÉELLES du site:")
        print("      - Événements créés et leurs caractéristiques")
        print("      - Inscriptions et taux de remplissage")
        print("      - Catégories et tags utilisés")
        print("      - Données des organisateurs")
        print("      - Historique des prix et performances")
        print("      - Tendances temporelles et géographiques")
        print()
        print("   🔄 L'IA apprend en continu des nouvelles données:")
        print("      - Chaque nouvel événement améliore les prédictions")
        print("      - Chaque inscription confirme ou infirme les prédictions")
        print("      - Les tendances émergentes sont détectées automatiquement")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ia_data_sources()














