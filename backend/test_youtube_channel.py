"""
Script simple pour tester l'API YouTube et trouver la vraie chaîne
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from googleapiclient.discovery import build

def test_youtube_api():
    """Test simple de l'API YouTube"""
    print("🎥 Test simple de l'API YouTube")
    print("=" * 40)
    
    # Votre clé API
    api_key = 'AIzaSyBuatB1Mqikc9-f0q7oMshAxDdeU0xD3F0'
    
    try:
        # Créer le service YouTube
        youtube = build('youtube', 'v3', developerKey=api_key)
        print("✅ Service YouTube créé avec succès")
        
        # Test 1: Rechercher votre chaîne par nom d'utilisateur
        print("\n🔍 Test 1: Recherche par nom d'utilisateur")
        search_response = youtube.search().list(
            part="snippet",
            q="KossiEmmanuelDOVON",
            type="channel",
            maxResults=5
        ).execute()
        
        print(f"Résultats trouvés: {len(search_response.get('items', []))}")
        for i, item in enumerate(search_response.get('items', [])):
            snippet = item['snippet']
            print(f"  {i+1}. {snippet['title']} (ID: {item['id']['channelId']})")
            print(f"     Description: {snippet['description'][:100]}...")
        
        # Test 2: Essayer de récupérer les détails d'une chaîne trouvée
        if search_response.get('items'):
            channel_id = search_response['items'][0]['id']['channelId']
            print(f"\n🔍 Test 2: Détails de la chaîne {channel_id}")
            
            channel_response = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            ).execute()
            
            if channel_response.get('items'):
                channel = channel_response['items'][0]
                print(f"✅ Chaîne trouvée: {channel['snippet']['title']}")
                print(f"   ID: {channel['id']}")
                print(f"   Abonnés: {channel['statistics'].get('subscriberCount', 'N/A')}")
                print(f"   Vidéos: {channel['statistics'].get('videoCount', 'N/A')}")
                print(f"   Vues: {channel['statistics'].get('viewCount', 'N/A')}")
                print(f"   URL personnalisée: {channel['snippet'].get('customUrl', 'N/A')}")
            else:
                print("❌ Aucun détail de chaîne trouvé")
        
        # Test 3: Recherche par URL de chaîne
        print("\n🔍 Test 3: Recherche par URL de chaîne")
        custom_urls = [
            "KossiEmmanuelDOVON",
            "@KossiEmmanuelDOVON",
            "kossiemmanueldovon"
        ]
        
        for custom_url in custom_urls:
            try:
                search_response = youtube.search().list(
                    part="snippet",
                    q=custom_url,
                    type="channel",
                    maxResults=3
                ).execute()
                
                print(f"Recherche '{custom_url}': {len(search_response.get('items', []))} résultats")
                for item in search_response.get('items', []):
                    snippet = item['snippet']
                    print(f"  - {snippet['title']} (ID: {item['id']['channelId']})")
            except Exception as e:
                print(f"Erreur recherche '{custom_url}': {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_youtube_api()
    sys.exit(0 if success else 1)

