#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.db import connection

def clean_phone_duplicates():
    """Nettoie les doublons de téléphone directement en SQL"""
    print("🔧 Nettoyage des doublons de téléphone...")
    
    with connection.cursor() as cursor:
        # Trouver les doublons
        cursor.execute("""
            SELECT event_id, guest_phone, COUNT(*) as count
            FROM events_eventregistration 
            WHERE guest_phone IS NOT NULL AND guest_phone != ''
            GROUP BY event_id, guest_phone 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        print(f"📱 Trouvé {len(duplicates)} groupes de doublons")
        
        for event_id, phone, count in duplicates:
            print(f"📱 Événement {event_id}, Téléphone {phone}: {count} inscriptions")
            
            # Garder la première inscription, supprimer les autres
            cursor.execute("""
                DELETE FROM events_eventregistration 
                WHERE event_id = %s AND guest_phone = %s 
                AND id NOT IN (
                    SELECT MIN(id) 
                    FROM events_eventregistration 
                    WHERE event_id = %s AND guest_phone = %s
                )
            """, [event_id, phone, event_id, phone])
            
            deleted_count = cursor.rowcount
            print(f"🗑️ Suppression de {deleted_count} doublons")
    
    print("✅ Nettoyage terminé!")

if __name__ == '__main__':
    clean_phone_duplicates()



