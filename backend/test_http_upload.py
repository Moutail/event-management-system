#!/usr/bin/env python
"""
Script de test pour simuler une requête HTTP avec upload d'image
"""
import requests
import os
from pathlib import Path

def test_http_upload():
    """Test d'upload via HTTP"""
    print("=== Test d'upload HTTP ===")
    
    # URL de l'API
    base_url = "http://localhost:8000/api"
    login_url = f"{base_url}/token/"
    events_url = f"{base_url}/events/"
    
    # Créer un fichier image de test (vraie image JPEG)
    test_image_path = "test_upload.jpg"
    # Contenu d'une vraie image JPEG (1x1 pixel)
    jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    with open(test_image_path, "wb") as f:
        f.write(jpeg_content)
    
    print(f"Fichier de test créé: {test_image_path}")
    
    try:
        # 1. Authentification
        print("1. Authentification...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = requests.post(login_url, data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Échec de l'authentification: {login_response.text}")
            return
        
        token = login_response.json()['access']
        print(f"✅ Token obtenu: {token[:20]}...")
        
        # Headers avec authentification
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # 2. Upload de l'événement avec image
        print("2. Upload de l'événement...")
        data = {
            'title': 'Test Event HTTP',
            'description': 'Test description',
            'start_date': '2025-01-01T10:00:00Z',
            'end_date': '2025-01-01T12:00:00Z',
            'location': 'Test Location',
            'is_free': 'true',
            'price': '0',
            'is_featured': 'false',
            'is_public': 'true',
        }
        
        # Fichier à uploader
        with open(test_image_path, 'rb') as f:
            files = {
                'poster': ('test_image.jpg', f, 'image/jpeg')
            }
            
            response = requests.post(events_url, data=data, files=files, headers=headers)
        
        print(f"Upload Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 201:
            print("✅ Upload réussi!")
        else:
            print("❌ Upload échoué!")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        # Nettoyer le fichier de test
        try:
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                print(f"Fichier de test supprimé: {test_image_path}")
        except:
            pass

if __name__ == '__main__':
    test_http_upload() 