#!/usr/bin/env python
"""
Test rapide de l'API via HTTP
"""
import requests

def test_api():
    """Tester l'API via HTTP"""
    print("🧪 Test rapide de l'API sur le port 8000...")
    
    try:
        # Test de l'API des statistiques globales
        response = requests.get('http://localhost:8000/api/admin/global_stats/')
        print(f"📊 API Statistiques - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Données reçues: {len(data)} champs")
        elif response.status_code == 401:
            print("   🔒 Authentification requise (normal)")
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur sur le port 8000")
        print("   Vérifiez que le serveur est démarré")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n🎯 Test terminé!")

if __name__ == '__main__':
    test_api()
