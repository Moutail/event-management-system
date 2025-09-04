"""
Test détaillé pour diagnostiquer le problème Zoom
"""

import os
import sys
import django
import requests
import base64
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def test_zoom_authentication():
    """Test détaillé de l'authentification Zoom"""
    print("🎥 Test détaillé de l'authentification Zoom")
    print("=" * 60)
    
    # Vos credentials Zoom
    account_id = 'CfLVvpjDSnqvZQBIVuixVA'
    client_id = 'Fei6YofJS1CGOiGTiJCMoA'
    client_secret = 'bwzivYmbSKaHloGylA684oqWSQCjgIaR'
    
    print(f"Account ID: {account_id}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    
    try:
        # Encoder les credentials
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        print(f"\n🔐 Credentials encodés: {encoded_credentials[:20]}...")
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "account_credentials",
            "account_id": account_id
        }
        
        print("\n📤 Envoi de la requête d'authentification...")
        print(f"URL: https://zoom.us/oauth/token")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(
            "https://zoom.us/oauth/token",
            headers=headers,
            data=data,
            timeout=30
        )
        
        print(f"\n📥 Réponse reçue:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Essayer de parser la réponse
        try:
            response_json = response.json()
            print(f"JSON Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Text Response: {response.text}")
        
        # Analyse de la réponse
        if response.status_code == 200:
            print("\n✅ AUTHENTIFICATION RÉUSSIE !")
            access_token = response_json.get('access_token', '')
            expires_in = response_json.get('expires_in', 0)
            print(f"Access Token: {access_token[:20]}...")
            print(f"Expire dans: {expires_in} secondes")
            
            # Test de l'API avec le token
            print("\n🧪 Test de l'API avec le token...")
            test_zoom_api(access_token)
            
        elif response.status_code == 400:
            print("\n❌ ERREUR 400 - Bad Request")
            if 'invalid_client' in response.text:
                print("🔍 Problème: 'invalid_client'")
                print("💡 Solutions possibles:")
                print("   1. Vérifiez que l'App Zoom est activée")
                print("   2. Vérifiez les scopes dans l'onglet 'Scopes'")
                print("   3. Vérifiez que l'App est publiée")
                print("   4. Attendez que l'App soit approuvée par Zoom")
            elif 'invalid_grant' in response.text:
                print("🔍 Problème: 'invalid_grant'")
                print("💡 Vérifiez le grant_type et account_id")
            else:
                print("🔍 Autre erreur 400 - vérifiez la requête")
                
        elif response.status_code == 401:
            print("\n❌ ERREUR 401 - Unauthorized")
            print("💡 Vérifiez vos credentials")
            
        elif response.status_code == 403:
            print("\n❌ ERREUR 403 - Forbidden")
            print("💡 L'App n'a pas les permissions nécessaires")
            
        else:
            print(f"\n❌ ERREUR {response.status_code} - Inconnue")
            
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de la requête")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_zoom_api(access_token):
    """Test de l'API Zoom avec le token"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Récupérer les informations utilisateur
        print("   🔍 Test 1: Informations utilisateur...")
        response = requests.get(
            "https://api.zoom.us/v2/users/me",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"      ✅ Utilisateur: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
            print(f"      📧 Email: {user_data.get('email', '')}")
            print(f"      🆔 ID: {user_data.get('id', '')}")
        else:
            print(f"      ❌ Erreur: {response.status_code}")
            
        # Test 2: Récupérer les réunions
        print("   🔍 Test 2: Liste des réunions...")
        response = requests.get(
            "https://api.zoom.us/v2/users/me/meetings",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            meetings_data = response.json()
            meetings_count = len(meetings_data.get('meetings', []))
            print(f"      ✅ Réunions trouvées: {meetings_count}")
        else:
            print(f"      ❌ Erreur: {response.status_code}")
            
    except Exception as e:
        print(f"      ❌ Erreur test API: {e}")

if __name__ == "__main__":
    success = test_zoom_authentication()
    sys.exit(0 if success else 1)

