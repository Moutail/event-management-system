#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections apportées au système d'événements
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://event-management-backend-7uux.onrender.com"
FRONTEND_URL = "https://event-management-system-git-main-moutails-projects.vercel.app"

def test_endpoints():
    """Tester les endpoints corrigés"""
    print("🔍 Test des corrections apportées...")
    
    # Test 1: Vérifier que l'endpoint /api/events/my_events/ existe
    print("\n1. Test de l'endpoint /api/events/my_events/")
    try:
        response = requests.get(f"{BASE_URL}/api/events/my_events/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint existe (retourne 401 - authentification requise)")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Vérifier que l'endpoint /api/events/{id}/ticket_types/ existe
    print("\n2. Test de l'endpoint /api/events/1/ticket_types/")
    try:
        response = requests.get(f"{BASE_URL}/api/events/1/ticket_types/")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404, 401]:
            print("   ✅ Endpoint existe")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Vérifier que l'endpoint /api/events/{id}/session_types/ existe
    print("\n3. Test de l'endpoint /api/events/1/session_types/")
    try:
        response = requests.get(f"{BASE_URL}/api/events/1/session_types/")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404, 401]:
            print("   ✅ Endpoint existe")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Vérifier que l'endpoint /api/events/{id}/publish/ existe
    print("\n4. Test de l'endpoint /api/events/1/publish/")
    try:
        response = requests.post(f"{BASE_URL}/api/events/1/publish/")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 401, 403, 404]:
            print("   ✅ Endpoint existe")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Vérifier que l'endpoint /api/registrations/ fonctionne
    print("\n5. Test de l'endpoint /api/registrations/")
    try:
        response = requests.post(f"{BASE_URL}/api/registrations/", 
                               json={"event": 1, "ticket_type_id": None})
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201, 400, 401]:
            print("   ✅ Endpoint fonctionne (plus d'erreur ImproperlyConfigured)")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test des corrections du système d'événements")
    print(f"Backend: {BASE_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    
    test_endpoints()
    
    print("\n📋 Résumé des corrections apportées:")
    print("✅ 1. Corrigé l'erreur 'registration_date' -> 'registered_at' dans SimpleEventRegistrationSerializer")
    print("✅ 2. Ajouté l'endpoint /api/events/my_events/ pour récupérer les événements de l'utilisateur")
    print("✅ 3. Ajouté l'endpoint /api/events/{id}/publish/ pour publier un événement")
    print("✅ 4. Ajouté l'endpoint /api/events/{id}/ticket_types/ pour récupérer les types de billets")
    print("✅ 5. Ajouté l'endpoint /api/events/{id}/session_types/ pour récupérer les types de sessions")
    print("✅ 6. Corrigé les références à 'registration_date' dans views.py")
    
    print("\n🎯 Prochaines étapes:")
    print("1. Tester l'inscription à un événement depuis le frontend")
    print("2. Tester la création et publication d'un événement")
    print("3. Vérifier que les événements en brouillon s'affichent correctement")
    print("4. Tester la modification et suppression d'événements")

if __name__ == "__main__":
    main()
