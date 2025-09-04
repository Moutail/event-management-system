#!/usr/bin/env python3
"""
Test du système complet : inscription → identifiants → mail
"""

import os
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent, EventRegistration
from events.emails import send_event_confirmation_email
from django.contrib.auth.models import User
from django.utils import timezone

def test_complete_system():
    """Test du système complet d'inscription et d'envoi de mails"""
    print("=== TEST DU SYSTEME COMPLET ===\n")
    
    try:
        # 1. Vérifier l'événement CONFEMMA2
        print("1. Vérification de l'événement CONFEMMA2...")
        event = Event.objects.get(title="CONFEMMA2")
        print(f"   ✅ Event trouvé: {event.title}")
        print(f"   Type: {event.event_type}")
        print(f"   Organisateur: {event.organizer.username}")
        
        # 2. Vérifier le VirtualEvent et ses identifiants
        print(f"\n2. Vérification du VirtualEvent et identifiants...")
        try:
            virtual_event = event.virtual_details
            print(f"   ✅ VirtualEvent trouvé: ID {virtual_event.id}")
            print(f"   Platform: {virtual_event.platform}")
            print(f"   Meeting ID: {virtual_event.meeting_id}")
            print(f"   Meeting URL: {virtual_event.meeting_url}")
            print(f"   Meeting Password: {virtual_event.meeting_password}")
            
            # Vérifier si les identifiants sont complets
            if virtual_event.meeting_id and virtual_event.meeting_url:
                print(f"   ✅ Identifiants complets")
            else:
                print(f"   ⚠️ Identifiants incomplets")
                if not virtual_event.meeting_id:
                    print(f"      - Meeting ID manquant")
                if not virtual_event.meeting_url:
                    print(f"      - Meeting URL manquante")
                    
        except VirtualEvent.DoesNotExist:
            print(f"   ❌ Aucun VirtualEvent configuré")
            return
        
        # 3. Vérifier les inscriptions et leurs statuts
        print(f"\n3. Vérification des inscriptions...")
        registrations = EventRegistration.objects.filter(event=event)
        print(f"   Total inscriptions: {registrations.count()}")
        
        for reg in registrations:
            print(f"   - {reg.user.username}: {reg.status}")
            print(f"     Email: {reg.user.email}")
            print(f"     Créé: {reg.created_at}")
            print(f"     Mis à jour: {reg.updated_at}")
        
        # 4. Tester l'envoi de mail de confirmation
        print(f"\n4. Test de l'envoi de mail de confirmation...")
        
        # Trouver une inscription confirmée
        confirmed_reg = registrations.filter(status='confirmed').first()
        if confirmed_reg:
            print(f"   Test avec l'inscription de {confirmed_reg.user.username}")
            print(f"   Email: {confirmed_reg.user.email}")
            
            try:
                # Tester l'envoi du mail
                result = send_event_confirmation_email(confirmed_reg)
                print(f"   ✅ Mail envoyé avec succès: {result}")
            except Exception as e:
                print(f"   ❌ Erreur envoi mail: {e}")
        else:
            print(f"   ⚠️ Aucune inscription confirmée trouvée pour tester")
        
        # 5. Vérifier la génération automatique des identifiants
        print(f"\n5. Vérification de la génération des identifiants...")
        
        if virtual_event.platform == 'youtube_live':
            print(f"   Platform YouTube Live:")
            print(f"     - Meeting ID devrait être généré automatiquement")
            print(f"     - Meeting URL devrait être: https://youtube.com/live/[MEETING_ID]")
        elif virtual_event.platform == 'zoom':
            print(f"   Platform Zoom:")
            print(f"     - Meeting ID devrait être généré via l'API Zoom")
            print(f"     - Meeting URL devrait être: https://zoom.us/j/[MEETING_ID]")
        
        # 6. Vérifier le processus d'inscription
        print(f"\n6. Vérification du processus d'inscription...")
        
        # Simuler une nouvelle inscription
        test_user = User.objects.filter(username__startswith='test').first()
        if test_user:
            print(f"   Test avec utilisateur: {test_user.username}")
            
            # Vérifier s'il est déjà inscrit
            existing_reg = registrations.filter(user=test_user).first()
            if existing_reg:
                print(f"   - Déjà inscrit avec status: {existing_reg.status}")
            else:
                print(f"   - Pas encore inscrit")
                
                # Créer une inscription de test
                test_reg = EventRegistration.objects.create(
                    event=event,
                    user=test_user,
                    status='pending'
                )
                print(f"   - Inscription de test créée: {test_reg.id}")
                
                # Simuler la confirmation
                test_reg.status = 'confirmed'
                test_reg.save()
                print(f"   - Inscription confirmée")
                
                # Tester l'envoi du mail
                try:
                    result = send_event_confirmation_email(test_reg)
                    print(f"   - Mail de confirmation envoyé: {result}")
                except Exception as e:
                    print(f"   - Erreur envoi mail: {e}")
                
                # Nettoyer
                test_reg.delete()
                print(f"   - Inscription de test supprimée")
        else:
            print(f"   ⚠️ Aucun utilisateur de test trouvé")
        
        print("\n=== TESTS TERMINES ===")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_system()
