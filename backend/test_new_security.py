#!/usr/bin/env python3
"""
Test de la nouvelle interface de sécurité du streaming
Vérifie le formulaire de vérification des identifiants
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, User
from events.views import get_stream_access_form
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_new_security_interface():
    """Test de la nouvelle interface de sécurité"""
    print("=== TEST DE LA NOUVELLE INTERFACE DE SÉCURITÉ ===\n")
    
    try:
        # 1. Récupérer l'événement CONFER1
        print("1. Récupération de l'événement CONFER1...")
        event = Event.objects.get(title="CONFER1")
        print(f"   ✅ Événement trouvé: {event.title}")
        print(f"   Type: {event.event_type}")
        print(f"   Organisateur: {event.organizer.username}")
        
        # 2. Récupérer différents utilisateurs
        print(f"\n2. Récupération des utilisateurs...")
        
        # Utilisateur avec inscription payée
        try:
            user_paid = User.objects.get(username="nealdov7")
            print(f"   ✅ Utilisateur payé: {user_paid.username}")
        except User.DoesNotExist:
            print(f"   ❌ Utilisateur nealdov7 non trouvé")
            return
        
        # Utilisateur sans inscription
        try:
            user_not_registered = User.objects.get(username="xchak475")
            print(f"   ✅ Utilisateur non inscrit: {user_not_registered.username}")
        except User.DoesNotExist:
            print(f"   ❌ Utilisateur xchak475 non trouvé")
            return
        
        # 3. Créer une factory de requêtes pour simuler les appels API
        print(f"\n3. Test de l'interface de sécurité...")
        factory = RequestFactory()
        
        # Test avec utilisateur payé
        print(f"\n   Test avec {user_paid.username} (inscrit et payé):")
        request_paid = factory.get(f'/api/events/{event.id}/stream-access-form/')
        request_paid.user = user_paid
        
        try:
            response_paid = get_stream_access_form(request_paid, event.id)
            print(f"   Status Code: {response_paid.status_code}")
            
            if response_paid.status_code == 200:
                data = response_paid.data
                print(f"   ✅ SUCCÈS: Formulaire affiché")
                print(f"   Message: {data.get('message')}")
                print(f"   Vérification requise: {data.get('form_data', {}).get('verification_required')}")
                print(f"   Meeting ID: {data.get('form_data', {}).get('meeting_id')}")
                print(f"   Meeting URL: {data.get('form_data', {}).get('meeting_url')}")
                print(f"   Mot de passe: {data.get('form_data', {}).get('meeting_password')}")
                print(f"   Code d'accès: {data.get('form_data', {}).get('access_code')}")
            else:
                print(f"   ❌ ÉCHEC: {response_paid.data.get('error')}")
                
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
        
        # Test avec utilisateur non inscrit
        print(f"\n   Test avec {user_not_registered.username} (non inscrit):")
        request_not_registered = factory.get(f'/api/events/{event.id}/stream-access-form/')
        request_not_registered.user = user_not_registered
        
        try:
            response_not_registered = get_stream_access_form(request_not_registered, event.id)
            print(f"   Status Code: {response_not_registered.status_code}")
            
            if response_not_registered.status_code == 403:
                data = response_not_registered.data
                print(f"   ✅ SÉCURISATION OK: Accès refusé")
                print(f"   Erreur: {data.get('error')}")
                print(f"   Action requise: {data.get('action_required')}")
            else:
                print(f"   ❌ BRÈCHE DE SÉCURITÉ: Accès autorisé (Status {response_not_registered.status_code})")
                print(f"   Réponse: {response_not_registered.data}")
                
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
        
        # 4. Résumé de sécurité
        print(f"\n4. RÉSUMÉ DE LA NOUVELLE SÉCURISATION:")
        print(f"   🔒 Interface de vérification: {'✅ CRÉÉE' if 'get_stream_access_form' in dir() else '❌ MANQUANTE'}")
        print(f"   📋 Formulaire pour utilisateurs payés: {'✅ FONCTIONNE' if response_paid.status_code == 200 else '❌ PROBLÈME'}")
        print(f"   🚫 Blocage utilisateurs non payés: {'✅ FONCTIONNE' if response_not_registered.status_code == 403 else '❌ BRÈCHE'}")
        
        print("\n=== TEST TERMINÉ ===")
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_security_interface()
