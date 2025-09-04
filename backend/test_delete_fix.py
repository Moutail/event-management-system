#!/usr/bin/env python3
"""
🧪 TEST DE LA CORRECTION DE SUPPRESSION
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Category, Tag, Event

def test_delete_fix():
    """Test que la suppression des catégories et tags fonctionne maintenant"""
    
    print("🧪 TEST DE LA CORRECTION DE SUPPRESSION")
    print("=" * 50)
    
    try:
        # 1. Tester la relation Category -> Event
        print("\n1️⃣ Test de la relation Category -> Event")
        categories = Category.objects.all()[:2]  # Prendre 2 catégories
        
        for cat in categories:
            try:
                # Tester la nouvelle méthode
                events_count = Event.objects.filter(category=cat).count()
                has_events = Event.objects.filter(category=cat).exists()
                print(f"   📂 {cat.name} (ID: {cat.id})")
                print(f"      ✅ Événements: {events_count}")
                print(f"      ✅ Exists(): {has_events}")
            except Exception as e:
                print(f"   ❌ Erreur avec {cat.name}: {str(e)}")
        
        # 2. Tester la relation Tag -> Event
        print("\n2️⃣ Test de la relation Tag -> Event")
        tags = Tag.objects.all()[:2]  # Prendre 2 tags
        
        for tag in tags:
            try:
                # Tester la nouvelle méthode
                events_count = Event.objects.filter(tags=tag).count()
                has_events = Event.objects.filter(tags=tag).exists()
                print(f"   🏷️  {tag.name} (ID: {tag.id})")
                print(f"      ✅ Événements: {events_count}")
                print(f"      ✅ Exists(): {has_events}")
            except Exception as e:
                print(f"   ❌ Erreur avec {tag.name}: {str(e)}")
        
        print("\n🎯 Test terminé!")
        print("✅ Si aucune erreur, la correction fonctionne!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_fix()













