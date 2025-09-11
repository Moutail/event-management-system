#!/usr/bin/env python
"""
Script pour résoudre les conflits de migrations
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def fix_migrations():
    """Résoudre les conflits de migrations"""
    print("🔧 Résolution des conflits de migrations...")
    
    try:
        # 1. Fusionner les migrations
        print("1️⃣ Fusion des migrations...")
        call_command('makemigrations', '--merge', interactive=False)
        print("✅ Migrations fusionnées")
        
        # 2. Appliquer les migrations
        print("2️⃣ Application des migrations...")
        call_command('migrate', interactive=False)
        print("✅ Migrations appliquées")
        
        # 3. Créer le super admin
        print("3️⃣ Création du super admin...")
        call_command('create_superadmin')
        print("✅ Super admin créé")
        
        print("\n🎉 Toutes les migrations ont été résolues !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_migrations()
