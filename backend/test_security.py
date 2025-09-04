#!/usr/bin/env python3
"""
Test de sécurité du système de streaming
Vérifie que seuls les utilisateurs payants peuvent accéder
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, User
from events.streaming_views import _verify_payment_access

def test_security():
    """Test de la sécurité du streaming"""
    print("=== TEST DE SÉCURITÉ DU STREAMING ===\n")
    
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
        
        # 3. Vérifier les inscriptions
        print(f"\n3. Vérification des inscriptions...")
        
        # Inscription de l'utilisateur payé
        try:
            reg_paid = EventRegistration.objects.get(
                event=event,
                user=user_paid
            )
            print(f"   ✅ Inscription trouvée pour {user_paid.username}")
            print(f"   Status: {reg_paid.status}")
            print(f"   Paiement: {reg_paid.payment_status}")
        except EventRegistration.DoesNotExist:
            print(f"   ❌ Aucune inscription pour {user_paid.username}")
            return
        
        # Inscription de l'utilisateur non inscrit
        try:
            reg_not_registered = EventRegistration.objects.get(
                event=event,
                user=user_not_registered
            )
            print(f"   ✅ Inscription trouvée pour {user_not_registered.username}")
            print(f"   Status: {reg_not_registered.status}")
            print(f"   Paiement: {reg_not_registered.payment_status}")
        except EventRegistration.DoesNotExist:
            print(f"   ❌ Aucune inscription pour {user_not_registered.username} (normal)")
        
        # 4. Test de la fonction de vérification
        print(f"\n4. Test de la fonction de vérification...")
        
        # Test utilisateur payé
        print(f"\n   Test avec {user_paid.username} (inscrit et payé):")
        result_paid = _verify_payment_access(user_paid, event)
        if result_paid:
            print(f"   ✅ ACCÈS AUTORISÉ - Utilisateur payé")
        else:
            print(f"   ❌ ACCÈS REFUSÉ - Utilisateur payé (PROBLÈME!)")
        
        # Test utilisateur non inscrit
        print(f"\n   Test avec {user_not_registered.username} (non inscrit):")
        result_not_registered = _verify_payment_access(user_not_registered, event)
        if result_not_registered:
            print(f"   ❌ ACCÈS AUTORISÉ - Utilisateur non inscrit (BRÈCHE DE SÉCURITÉ!)")
        else:
            print(f"   ✅ ACCÈS REFUSÉ - Utilisateur non inscrit (SÉCURISATION OK)")
        
        # 5. Résumé de sécurité
        print(f"\n5. RÉSUMÉ DE SÉCURITÉ:")
        print(f"   🔒 Utilisateur payé: {'✅ AUTORISÉ' if result_paid else '❌ REFUSÉ'}")
        print(f"   🚫 Utilisateur non inscrit: {'❌ AUTORISÉ (BRÈCHE!)' if result_not_registered else '✅ REFUSÉ (SÉCURISÉ)'}")
        
        if result_paid and not result_not_registered:
            print(f"\n🎉 SÉCURISATION PARFAITE !")
            print(f"   - Les utilisateurs payés peuvent accéder")
            print(f"   - Les utilisateurs non payés sont bloqués")
        else:
            print(f"\n🚨 PROBLÈME DE SÉCURITÉ DÉTECTÉ !")
            if not result_paid:
                print(f"   - Les utilisateurs payés sont bloqués (PROBLÈME!)")
            if result_not_registered:
                print(f"   - Les utilisateurs non payés peuvent accéder (BRÈCHE!)")
        
        print("\n=== TEST TERMINÉ ===")
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_security()
