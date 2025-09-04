#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC DE L'ERREUR DE SUPPRESSION
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Category, Tag, Event
from django.db import connection

def diagnose_delete_error():
    """Diagnostique l'erreur de suppression des catégories et tags"""
    
    print("🔍 DIAGNOSTIC DE L'ERREUR DE SUPPRESSION")
    print("=" * 50)
    
    try:
        # 1. Vérifier l'état des modèles
        print("\n1️⃣ ÉTAT DES MODÈLES")
        print(f"   Catégories totales: {Category.objects.count()}")
        print(f"   Tags totaux: {Tag.objects.count()}")
        print(f"   Événements totaux: {Event.objects.count()}")
        
        # 2. Vérifier les catégories avec leurs événements
        print("\n2️⃣ CATÉGORIES ET LEURS ÉVÉNEMENTS")
        categories = Category.objects.all()
        for cat in categories:
            try:
                events_count = cat.events.count()
                print(f"   📂 {cat.name} (ID: {cat.id}) - Événements: {events_count}")
                
                # Tester la relation exists()
                try:
                    has_events = cat.events.exists()
                    print(f"      ✅ exists() fonctionne: {has_events}")
                except Exception as e:
                    print(f"      ❌ exists() échoue: {str(e)}")
                    
            except Exception as e:
                print(f"   ❌ Erreur avec catégorie {cat.id}: {str(e)}")
        
        # 3. Vérifier les tags avec leurs événements
        print("\n3️⃣ TAGS ET LEURS ÉVÉNEMENTS")
        tags = Tag.objects.all()
        for tag in tags:
            try:
                events_count = tag.events.count()
                print(f"   🏷️  {tag.name} (ID: {tag.id}) - Événements: {events_count}")
                
                # Tester la relation exists()
                try:
                    has_events = tag.events.exists()
                    print(f"      ✅ exists() fonctionne: {has_events}")
                except Exception as e:
                    print(f"      ❌ exists() échoue: {str(e)}")
                    
            except Exception as e:
                print(f"   ❌ Erreur avec tag {tag.id}: {str(e)}")
        
        # 4. Vérifier la base de données
        print("\n4️⃣ VÉRIFICATION DE LA BASE DE DONNÉES")
        with connection.cursor() as cursor:
            # Vérifier la table des événements
            cursor.execute("SELECT COUNT(*) FROM events_event")
            events_count = cursor.fetchone()[0]
            print(f"   📊 Table events_event: {events_count} enregistrements")
            
            # Vérifier la table des catégories
            cursor.execute("SELECT COUNT(*) FROM events_category")
            categories_count = cursor.fetchone()[0]
            print(f"   📊 Table events_category: {categories_count} enregistrements")
            
            # Vérifier la table des tags
            cursor.execute("SELECT COUNT(*) FROM events_tag")
            tags_count = cursor.fetchone()[0]
            print(f"   📊 Table events_tag: {tags_count} enregistrements")
            
            # Vérifier la table de liaison tags-événements
            cursor.execute("SELECT COUNT(*) FROM events_event_tags")
            tags_events_count = cursor.fetchone()[0]
            print(f"   📊 Table events_event_tags: {tags_events_count} enregistrements")
            
            # Vérifier les contraintes de clés étrangères
            print("\n5️⃣ VÉRIFICATION DES RELATIONS")
            
            # Test de la relation Category -> Event
            cursor.execute("""
                SELECT c.id, c.name, COUNT(e.id) as event_count
                FROM events_category c
                LEFT JOIN events_event e ON c.id = e.category_id
                GROUP BY c.id, c.name
                ORDER BY event_count DESC
            """)
            category_relations = cursor.fetchall()
            print("   🔗 Relations Category -> Event:")
            for cat_id, cat_name, event_count in category_relations:
                print(f"      {cat_name} (ID: {cat_id}): {event_count} événements")
            
            # Test de la relation Tag -> Event (via table de liaison)
            cursor.execute("""
                SELECT t.id, t.name, COUNT(et.event_id) as event_count
                FROM events_tag t
                LEFT JOIN events_event_tags et ON t.id = et.tag_id
                GROUP BY t.id, t.name
                ORDER BY event_count DESC
            """)
            tag_relations = cursor.fetchall()
            print("   🔗 Relations Tag -> Event:")
            for tag_id, tag_name, event_count in tag_relations:
                print(f"      {tag_name} (ID: {tag_id}): {event_count} événements")
        
        print("\n🎯 DIAGNOSTIC TERMINÉ!")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DU DIAGNOSTIC: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_delete_error()














