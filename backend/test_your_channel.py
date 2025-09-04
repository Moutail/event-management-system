"""
Test spécifique pour votre chaîne YouTube
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from googleapiclient.discovery import build

def test_your_channel():
    """Test spécifique pour votre chaîne YouTube"""
    print("🎥 Test de votre chaîne YouTube")
    print("=" * 50)
    
    # Votre clé API
    api_key = 'AIzaSyBuatB1Mqikc9-f0q7oMshAxDdeU0xD3F0'
    your_channel_id = 'UCPNajjuSZ-Qr2I7mMzIv4WA'
    
    try:
        # Créer le service YouTube
        youtube = build('youtube', 'v3', developerKey=api_key)
        print("✅ Service YouTube créé avec succès")
        
        # Test direct avec votre ID de chaîne
        print(f"\n🔍 Test direct avec votre ID: {your_channel_id}")
        
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=your_channel_id
        ).execute()
        
        print(f"Réponse brute: {response}")
        
        if 'items' in response and response['items']:
            channel = response['items'][0]
            print(f"✅ Chaîne trouvée: {channel['snippet']['title']}")
            print(f"   ID: {channel['id']}")
            print(f"   Description: {channel['snippet']['description'][:100]}...")
            print(f"   Pays: {channel['snippet'].get('country', 'N/A')}")
            print(f"   Langue: {channel['snippet'].get('defaultLanguage', 'N/A')}")
            print(f"   Abonnés: {channel['statistics'].get('subscriberCount', 'N/A')}")
            print(f"   Vidéos: {channel['statistics'].get('videoCount', 'N/A')}")
            print(f"   Vues: {channel['statistics'].get('viewCount', 'N/A')}")
            print(f"   URL personnalisée: {channel['snippet'].get('customUrl', 'N/A')}")
            print(f"   Date de création: {channel['snippet'].get('publishedAt', 'N/A')}")
            
            # Vérifier si la chaîne peut faire du live streaming
            print(f"\n📺 Informations de live streaming:")
            
            # Récupérer les informations de live streaming
            try:
                live_broadcasts = youtube.liveBroadcasts().list(
                    part="snippet,status",
                    channelId=your_channel_id,
                    maxResults=1
                ).execute()
                
                print(f"   Live broadcasts autorisés: {len(live_broadcasts.get('items', []))}")
                
            except Exception as live_error:
                print(f"   ⚠️ Erreur vérification live: {live_error}")
            
            return True
            
        else:
            print("❌ Aucune chaîne trouvée avec cet ID")
            print(f"Réponse complète: {response}")
            
            # Essayer de comprendre pourquoi
            if 'error' in response:
                print(f"Erreur API: {response['error']}")
            
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_your_channel()
    sys.exit(0 if success else 1)

