#!/usr/bin/env python
"""
🔍 SCRIPT DE VÉRIFICATION DES MIGRATIONS
Vérifie et applique les migrations sur Render
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def setup_django():
    """Configurer Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings_render')
    django.setup()

def check_migrations():
    """Vérifier les migrations"""
    print("🔍 VÉRIFICATION DES MIGRATIONS")
    print("=" * 50)
    
    try:
        # Vérifier les migrations en attente
        print("📋 Vérification des migrations en attente...")
        execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
        
        # Appliquer les migrations
        print("\n🗄️ Application des migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migrations appliquées avec succès")
        
        # Vérifier la connexion à la base de données
        print("\n🔗 Test de connexion à la base de données...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Connexion à la base de données réussie")
            else:
                print("❌ Problème de connexion à la base de données")
                return False
        
        # Vérifier les tables
        print("\n📊 Vérification des tables...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"✅ {len(tables)} tables trouvées:")
            for table in tables:
                print(f"   - {table[0]}")
        
        # Créer un superutilisateur si nécessaire
        print("\n👤 Vérification du superutilisateur...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@eventmanagement.com',
                password='admin123'
            )
            print("✅ Superutilisateur créé: admin/admin123")
        else:
            print("ℹ️ Superutilisateur existe déjà")
        
        print("\n🎉 VÉRIFICATION TERMINÉE AVEC SUCCÈS!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale"""
    setup_django()
    success = check_migrations()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
