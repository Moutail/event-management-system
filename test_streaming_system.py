#!/usr/bin/env python3
"""
Script de test pour le système de streaming des événements virtuels
Teste la création, le lancement et la gestion des streams
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, VirtualEvent, User
from events.streaming_service import StreamingService

def test_streaming_system():
    """Test complet du système de streaming"""
    print("🎥 TEST DU SYSTÈME DE STREAMING")
    print("=" * 50)
    
    try:
        # 1. Vérifier la configuration YouTube
        print("\n1. 🔍 Vérification de la configuration YouTube...")
        from events.youtube_service import YouTubeLiveService
        youtube_service = YouTubeLiveService()
        
        if youtube_service.youtube:
            print("✅ API YouTube initialisée avec succès")
            
            # Tester la récupération des informations de la chaîne
            channel_info = youtube_service.get_channel_info()
            if 'error' not in channel_info:
                print(f"✅ Chaîne YouTube trouvée: {channel_info.get('title', 'N/A')}")
                print(f"   ID: {channel_info.get('id', 'N/A')}")
                print(f"   Abonnés: {channel_info.get('subscriber_count', 'N/A')}")
            else:
                print(f"⚠️ Erreur chaîne YouTube: {channel_info.get('error')}")
        else:
            print("❌ API YouTube non initialisée")
            return False
        
        # 2. Vérifier la configuration Zoom
        print("\n2. 🔍 Vérification de la configuration Zoom...")
        from events.zoom_service import ZoomService
        zoom_service = ZoomService()
        
        if zoom_service.access_token:
            print("✅ API Zoom initialisée avec succès")
            print(f"   Account ID: {zoom_service.account_id}")
            print(f"   Client ID: {zoom_service.client_id}")
        else:
            print("⚠️ API Zoom non initialisée (peut être normal)")
            print("   Vérifiez les credentials Zoom dans les paramètres")
        
        # 3. Tester le service de streaming unifié
        print("\n3. 🔍 Test du service de streaming unifié...")
        streaming_service = StreamingService()
        print("✅ Service de streaming créé avec succès")
        
        # 4. Vérifier les événements virtuels existants
        print("\n4. 🔍 Vérification des événements virtuels existants...")
        virtual_events = VirtualEvent.objects.filter(event__event_type='virtual')
        
        if virtual_events.exists():
            print(f"✅ {virtual_events.count()} événement(s) virtuel(s) trouvé(s)")
            
            for ve in virtual_events[:3]:  # Tester les 3 premiers
                event = ve.event
                print(f"\n   📅 Événement: {event.title}")
                print(f"      Plateforme: {ve.platform}")
                print(f"      Date: {event.start_date}")
                print(f"      URL: {ve.meeting_url or 'Non configuré'}")
                print(f"      Instructions: {'Oui' if ve.access_instructions else 'Non'}")
                
                # Tester la génération d'instructions
                if ve.platform == 'youtube_live':
                    instructions = streaming_service._generate_youtube_instructions(ve, event)
                    print(f"      Instructions générées: {len(instructions)} caractères")
                elif ve.platform == 'zoom':
                    instructions = streaming_service._generate_zoom_instructions(ve, event)
                    print(f"      Instructions générées: {len(instructions)} caractères")
        else:
            print("⚠️ Aucun événement virtuel trouvé")
            
            # Créer un événement virtuel de test
            print("\n5. 🧪 Création d'un événement virtuel de test...")
            
            # Trouver un utilisateur organisateur
            organizer = User.objects.filter(profile__role='organizer').first()
            if not organizer:
                organizer = User.objects.first()
            
            if organizer:
                # Créer un événement de test
                test_event = Event.objects.create(
                    title="TEST STREAMING - " + datetime.now().strftime("%H:%M"),
                    description="Événement de test pour le système de streaming",
                    start_date=datetime.now() + timedelta(hours=1),
                    end_date=datetime.now() + timedelta(hours=3),
                    event_type='virtual',
                    organizer=organizer,
                    status='published',
                    max_participants=10
                )
                
                # Créer les détails virtuels
                virtual_event = VirtualEvent.objects.create(
                    event=test_event,
                    platform='youtube_live',
                    auto_record=True,
                    allow_chat=True,
                    allow_screen_sharing=False,
                    waiting_room=False
                )
                
                print(f"✅ Événement de test créé: {test_event.title}")
                print(f"   ID: {test_event.id}")
                print(f"   Organisateur: {organizer.username}")
                
                # Tester la création du stream
                print("\n6. 🧪 Test de création du stream...")
                try:
                    stream_info = streaming_service.create_stream_for_event(virtual_event)
                    
                    if stream_info and 'error' not in stream_info:
                        print("✅ Stream créé avec succès!")
                        print(f"   Plateforme: {stream_info.get('platform')}")
                        print(f"   URL: {stream_info.get('watch_url')}")
                        print(f"   Chat: {stream_info.get('chat_url')}")
                        
                        # Vérifier que l'événement virtuel a été mis à jour
                        virtual_event.refresh_from_db()
                        print(f"   Meeting ID: {virtual_event.meeting_id}")
                        print(f"   Meeting URL: {virtual_event.meeting_url}")
                        print(f"   Instructions: {'Oui' if virtual_event.access_instructions else 'Non'}")
                        
                    else:
                        error_msg = stream_info.get('error', 'Erreur inconnue') if stream_info else 'Pas de réponse'
                        print(f"❌ Erreur création stream: {error_msg}")
                        
                except Exception as e:
                    print(f"❌ Exception lors de la création du stream: {e}")
                
                # Nettoyer l'événement de test
                print("\n7. 🧹 Nettoyage de l'événement de test...")
                test_event.delete()
                print("✅ Événement de test supprimé")
        
        # 5. Test des instructions de connexion
        print("\n8. 🔍 Test de génération des instructions...")
        
        # Créer un événement temporaire pour le test
        temp_event = Event(
            title="Test Instructions",
            start_date=datetime.now() + timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=2)
        )
        
        temp_virtual = VirtualEvent(
            platform='youtube_live',
            meeting_url='https://www.youtube.com/watch?v=test123'
        )
        
        # Tester les instructions YouTube
        youtube_instructions = streaming_service._generate_youtube_instructions(temp_virtual, temp_event)
        print(f"✅ Instructions YouTube générées: {len(youtube_instructions)} caractères")
        
        # Tester les instructions Zoom
        temp_virtual.platform = 'zoom'
        temp_virtual.meeting_id = '123456789'
        temp_virtual.meeting_password = 'TestPass123'
        zoom_instructions = streaming_service._generate_zoom_instructions(temp_virtual, temp_event)
        print(f"✅ Instructions Zoom générées: {len(zoom_instructions)} caractères")
        
        print("\n" + "=" * 50)
        print("🎉 TESTS TERMINÉS AVEC SUCCÈS!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_streaming_system()
    sys.exit(0 if success else 1)
