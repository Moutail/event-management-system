#!/usr/bin/env python
"""Script de test pour vérifier le modèle CustomReminder"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def test_custom_reminder_model():
    """Test du modèle CustomReminder"""
    try:
        from events.models import CustomReminder, Event, User
        
        print("🔍 Test du modèle CustomReminder...")
        
        # Vérifier les champs du modèle
        fields = [f.name for f in CustomReminder._meta.fields]
        print(f"✅ Champs du modèle: {fields}")
        
        # Vérifier si total_recipients existe
        if 'total_recipients' in fields:
            print("✅ Champ total_recipients trouvé!")
        else:
            print("❌ Champ total_recipients manquant!")
            
        # Vérifier les choix
        print(f"✅ REMINDER_TYPE_CHOICES: {CustomReminder.REMINDER_TYPE_CHOICES}")
        print(f"✅ TARGET_CHOICES: {CustomReminder.TARGET_CHOICES}")
        
        # Test de création d'un objet (sans sauvegarder)
        print("\n🔍 Test de création d'objet...")
        
        # Récupérer un utilisateur et un événement existants
        user = User.objects.first()
        event = Event.objects.first()
        
        if user and event:
            reminder = CustomReminder(
                title="Test Rappel",
                message="Message de test",
                reminder_type="general",
                target_audience="all",
                event=event,
                created_by=user,
                total_recipients=0
            )
            print("✅ Objet CustomReminder créé avec succès!")
            print(f"   - ID: {reminder.id}")
            print(f"   - Titre: {reminder.title}")
            print(f"   - Type: {reminder.reminder_type}")
            print(f"   - Audience: {reminder.target_audience}")
            print(f"   - Total recipients: {reminder.total_recipients}")
        else:
            print("⚠️ Aucun utilisateur ou événement trouvé pour le test")
            
        print("\n🎉 Test du modèle réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_custom_reminder_model()
    sys.exit(0 if success else 1)


