#!/usr/bin/env python
"""
🗄️ SCRIPT DE MIGRATION DE BASE DE DONNÉES
Script pour migrer de SQLite vers PostgreSQL en production
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Configurer Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings_production')
    django.setup()

def migrate_database():
    """Migrer la base de données"""
    print("🗄️ MIGRATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    try:
        # Appliquer les migrations
        print("📋 Application des migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès")
        
        # Créer les groupes et permissions
        print("👥 Création des groupes et permissions...")
        execute_from_command_line(['manage.py', 'create_groups'])
        print("✅ Groupes créés avec succès")
        
        # Collecter les fichiers statiques
        print("📁 Collecte des fichiers statiques...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Fichiers statiques collectés")
        
        # Créer un superutilisateur par défaut
        print("👤 Création du superutilisateur...")
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
        
        print("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def main():
    """Fonction principale"""
    setup_django()
    success = migrate_database()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
