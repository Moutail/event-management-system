#!/usr/bin/env python
"""
Vérification que le serveur redémarré fonctionne
"""
import requests
import time

def verify_server():
    """Vérifier que le serveur fonctionne"""
    print("🔍 Vérification du serveur redémarré...")
    
    # Attendre un peu que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    try:
        # Test de l'API des statistiques globales
        response = requests.get('http://localhost:8000/api/admin/global_stats/')
        print(f"📊 API Statistiques - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCÈS ! Données reçues: {len(data)} champs")
            print(f"   📈 Total utilisateurs: {data.get('total_users', 'N/A')}")
            print(f"   🎪 Total événements: {data.get('total_events', 'N/A')}")
            print(f"   📝 Total inscriptions: {data.get('total_registrations', 'N/A')}")
            print(f"   💰 Total revenus: {data.get('total_revenue', 'N/A')}€")
        elif response.status_code == 401:
            print("   🔒 Authentification requise (normal)")
            print("   ✅ Le serveur fonctionne correctement !")
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur sur le port 8000")
        print("   Vérifiez que le serveur est démarré avec: python manage.py runserver 8000")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n🎯 Vérification terminée!")
    print("   - Si vous voyez 'SUCCÈS' ou 'Authentification requise', tout fonctionne !")
    print("   - Si vous voyez une erreur, le serveur doit être redémarré")

if __name__ == '__main__':
    verify_server()
