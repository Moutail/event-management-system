#!/usr/bin/env python3
"""
Script de test pour vérifier l'exportation des participants
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "username": "testadmin",
    "password": "test123"
}

def test_login():
    """Test de connexion super admin"""
    print("🔐 Test de connexion...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/token/", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            print("✅ Connexion réussie")
            return response.json().get('access')
        else:
            print(f"❌ Échec de la connexion: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_get_events(token):
    """Test de récupération des événements"""
    print("\n📋 Test de récupération des événements...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/events/", headers=headers)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ {len(events)} événements récupérés")
            print(f"   Type de réponse: {type(events)}")
            if isinstance(events, dict):
                print(f"   Clés: {list(events.keys())}")
                if 'results' in events:
                    events_list = events['results']
                    print(f"   Nombre d'événements dans 'results': {len(events_list)}")
                    return events_list
                else:
                    print(f"   Pas de clé 'results' trouvée")
                    return []
            elif isinstance(events, list):
                return events
            else:
                print(f"   Type de réponse inattendu: {type(events)}")
                return []
        else:
            print(f"❌ Échec de récupération des événements: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur de récupération des événements: {e}")
        return []

def test_event_detail(token, event_id):
    """Test de récupération des détails d'événement"""
    print(f"\n🔍 Test des détails de l'événement {event_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/events/{event_id}/detail/", headers=headers)
        print(f"   URL appelée: {BASE_URL}/api/admin/events/{event_id}/detail/")
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            event_data = response.json()
            print(f"✅ Détails de l'événement récupérés")
            
            # Vérifier la présence des données des participants
            if 'registrations' in event_data:
                print(f"✅ Section participants présente avec {len(event_data['registrations'])} participants")
                
                # Afficher les informations des participants
                for i, reg in enumerate(event_data['registrations'][:3]):  # Afficher les 3 premiers
                    print(f"  Participant {i+1}: {reg['user']['username']} - {reg['status']}")
                
                if len(event_data['registrations']) > 3:
                    print(f"  ... et {len(event_data['registrations']) - 3} autres")
            else:
                print("❌ Section participants manquante")
            
            # Vérifier les statistiques
            if 'registrations_stats' in event_data:
                stats = event_data['registrations_stats']
                print(f"✅ Statistiques: {stats['total']} total, {stats['confirmed']} confirmées")
            
            return event_data
        else:
            print(f"❌ Échec de récupération des détails: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de récupération des détails: {e}")
        return None

def test_export_csv(token, event_id):
    """Test d'export CSV"""
    print(f"\n📊 Test d'export CSV pour l'événement {event_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/events/{event_id}/export_csv/", 
            headers=headers,
            stream=True
        )
        
        if response.status_code == 200:
            # Vérifier le type de contenu
            content_type = response.headers.get('content-type', '')
            if 'text/csv' in content_type:
                print("✅ Export CSV réussi")
                print(f"   Type de contenu: {content_type}")
                
                # Vérifier le nom du fichier
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' in content_disposition:
                    print("✅ Fichier en téléchargement")
                    print(f"   Disposition: {content_disposition}")
                
                # Lire le contenu pour vérifier les données
                content = response.content.decode('utf-8')
                lines = content.split('\n')
                if len(lines) > 1:  # En-têtes + au moins une ligne de données
                    print(f"✅ Contenu CSV valide: {len(lines)} lignes")
                    print(f"   En-têtes: {lines[0]}")
                    if len(lines) > 1:
                        print(f"   Première ligne de données: {lines[1]}")
                else:
                    print("⚠️ CSV vide ou invalide")
                
                return True
            else:
                print(f"❌ Type de contenu incorrect: {content_type}")
                return False
        else:
            print(f"❌ Échec de l'export CSV: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur d'export CSV: {e}")
        return False

def test_export_excel(token, event_id):
    """Test d'export Excel"""
    print(f"\n📊 Test d'export Excel pour l'événement {event_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/events/{event_id}/export_excel/", 
            headers=headers,
            stream=True
        )
        
        if response.status_code == 200:
            # Vérifier le type de contenu
            content_type = response.headers.get('content-type', '')
            if 'spreadsheetml' in content_type or 'excel' in content_type:
                print("✅ Export Excel réussi")
                print(f"   Type de contenu: {content_type}")
                
                # Vérifier le nom du fichier
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' in content_disposition:
                    print("✅ Fichier en téléchargement")
                    print(f"   Disposition: {content_disposition}")
                
                # Vérifier la taille du contenu
                content_length = len(response.content)
                if content_length > 100:  # Fichier Excel minimal
                    print(f"✅ Contenu Excel valide: {content_length} octets")
                else:
                    print("⚠️ Fichier Excel trop petit, possiblement invalide")
                
                return True
            else:
                print(f"❌ Type de contenu incorrect: {content_type}")
                return False
        else:
            print(f"❌ Échec de l'export Excel: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur d'export Excel: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de l'exportation des participants")
    print("=" * 50)
    
    # Test de connexion
    token = test_login()
    if not token:
        print("❌ Impossible de continuer sans token d'authentification")
        return
    
    # Test de récupération des événements
    events = test_get_events(token)
    if not events:
        print("❌ Impossible de continuer sans événements")
        return
    
    # Prendre le premier événement avec des participants
    event_with_participants = None
    for event in events:
        if isinstance(event, dict) and event.get('registrations_count', 0) > 0:
            event_with_participants = event
            break
    
    if not event_with_participants:
        print("⚠️ Aucun événement avec des participants trouvé")
        # Prendre le premier événement disponible
        event_with_participants = events[0] if events else None
    
    if not event_with_participants:
        print("❌ Aucun événement disponible pour le test")
        return
    
    event_id = event_with_participants.get('id')
    event_title = event_with_participants.get('title', 'Sans titre')
    print(f"\n🎯 Test sur l'événement: {event_title} (ID: {event_id})")
    
    # Test des détails de l'événement
    event_details = test_event_detail(token, event_id)
    if not event_details:
        print("❌ Impossible de récupérer les détails de l'événement")
        return
    
    # Test d'export CSV
    csv_success = test_export_csv(token, event_id)
    
    # Test d'export Excel
    excel_success = test_export_excel(token, event_id)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    if event_details:
        print(f"✅ Détails de l'événement: OK")
        if 'registrations' in event_details:
            print(f"✅ Section participants: OK ({len(event_details['registrations'])} participants)")
        else:
            print("❌ Section participants: MANQUANTE")
    else:
        print("❌ Détails de l'événement: ÉCHEC")
    
    if csv_success:
        print("✅ Export CSV: OK")
    else:
        print("❌ Export CSV: ÉCHEC")
    
    if excel_success:
        print("✅ Export Excel: OK")
    else:
        print("❌ Export Excel: ÉCHEC")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("-" * 30)
    
    if 'registrations' not in event_details:
        print("🔧 Corriger la vue backend pour inclure les données des participants")
    
    if not csv_success:
        print("🔧 Vérifier la fonction d'export CSV et les permissions")
    
    if not excel_success:
        print("🔧 Vérifier la fonction d'export Excel et l'installation d'openpyxl")
    
    print("\n🎉 Test terminé!")

if __name__ == "__main__":
    main()
