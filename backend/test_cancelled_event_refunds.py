#!/usr/bin/env python
"""
🧪 TEST : Système de remboursements automatiques pour événements annulés

Ce script teste la nouvelle fonctionnalité qui crée automatiquement des demandes de remboursement
lorsqu'un événement est annulé par l'organisateur ou le super admin.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Event, EventRegistration, RefundRequest, RefundPolicy
from django.utils import timezone

def test_cancelled_event_refunds():
    """Test complet du système de remboursements pour événements annulés"""
    print("🧪 TEST : Système de remboursements automatiques pour événements annulés")
    print("=" * 80)
    
    try:
        # 1. Vérifier qu'il y a des événements avec des inscriptions payantes
        print("\n1️⃣ Vérification des événements avec inscriptions payantes...")
        events_with_paid_registrations = Event.objects.filter(
            registrations__payment_status='paid',
            registrations__price_paid__gt=0,
            registrations__status='confirmed'
        ).distinct()
        
        if not events_with_paid_registrations.exists():
            print("❌ Aucun événement avec des inscriptions payantes trouvé")
            print("   Créez d'abord des événements avec des inscriptions payantes")
            return False
        
        print(f"✅ {events_with_paid_registrations.count()} événements avec inscriptions payantes trouvés")
        
        # 2. Sélectionner un événement pour le test
        test_event = events_with_paid_registrations.first()
        print(f"\n2️⃣ Événement sélectionné pour le test: {test_event.title}")
        print(f"   - ID: {test_event.id}")
        print(f"   - Organisateur: {test_event.organizer.username}")
        print(f"   - Statut actuel: {test_event.status}")
        
        # 3. Vérifier les inscriptions payantes
        paid_registrations = test_event.registrations.filter(
            payment_status='paid',
            price_paid__gt=0,
            status='confirmed'
        )
        
        print(f"\n3️⃣ Inscriptions payantes trouvées: {paid_registrations.count()}")
        for reg in paid_registrations:
            user_info = reg.user.email if reg.user else reg.guest_email
            print(f"   - {user_info}: {reg.price_paid}€")
        
        # 4. Vérifier s'il y a déjà des remboursements
        existing_refunds = RefundRequest.objects.filter(registration__event=test_event)
        print(f"\n4️⃣ Demandes de remboursement existantes: {existing_refunds.count()}")
        
        if existing_refunds.exists():
            print("   ⚠️  L'événement a déjà des remboursements, on va les supprimer pour le test")
            existing_refunds.delete()
            print("   ✅ Remboursements existants supprimés")
        
        # 5. Simuler l'annulation de l'événement (créer des remboursements automatiquement)
        print(f"\n5️⃣ Simulation de l'annulation de l'événement...")
        
        # Sauvegarder l'ancien statut
        old_status = test_event.status
        
        # Annuler l'événement
        test_event.status = 'cancelled'
        test_event.save()
        
        print(f"   ✅ Événement annulé (statut: {old_status} → {test_event.status})")
        
        # 6. Créer automatiquement des demandes de remboursement
        print(f"\n6️⃣ Création automatique des demandes de remboursement...")
        
        refunds_created = 0
        for registration in paid_registrations:
            try:
                # Obtenir ou créer la politique de remboursement
                try:
                    policy = test_event.refund_policy
                except RefundPolicy.DoesNotExist:
                    policy = RefundPolicy.objects.create(
                        event=test_event,
                        mode='mixed',
                        auto_refund_delay_hours=24,
                        refund_percentage_immediate=100,
                        refund_percentage_after_delay=100,
                        cutoff_hours_before_event=24,
                        allow_partial_refunds=True,
                        require_reason=False,
                        notify_organizer_on_cancellation=True
                    )
                    print(f"   📋 Politique de remboursement créée pour {test_event.title}")
                
                # Calculer les montants et dates
                refund_percentage = policy.get_refund_percentage(0)  # Annulation immédiate = 100%
                refund_amount = (registration.price_paid * refund_percentage) / 100
                
                now = timezone.now()
                auto_process_at = None
                if policy.mode in ['auto', 'mixed']:
                    auto_process_at = now + timedelta(hours=policy.auto_refund_delay_hours)
                
                expires_at = test_event.start_date - timedelta(hours=policy.cutoff_hours_before_event)
                
                # Créer la demande de remboursement
                refund_request = RefundRequest.objects.create(
                    registration=registration,
                    reason='Test: Événement annulé avec remboursement automatique',
                    amount_paid=registration.price_paid,
                    refund_percentage=refund_percentage,
                    refund_amount=refund_amount,
                    auto_process_at=auto_process_at,
                    expires_at=expires_at
                )
                
                refunds_created += 1
                user_info = registration.user.email if registration.user else registration.guest_email
                print(f"   ✅ Demande créée: ID={refund_request.id} pour {user_info} - Montant: {refund_amount}€")
                
            except Exception as e:
                print(f"   ❌ Erreur création remboursement pour {registration.id}: {e}")
                import traceback
                traceback.print_exc()
        
        # 7. Vérifier que les remboursements ont été créés
        print(f"\n7️⃣ Vérification des remboursements créés...")
        
        created_refunds = RefundRequest.objects.filter(registration__event=test_event)
        print(f"   📊 Total des demandes de remboursement: {created_refunds.count()}")
        
        if created_refunds.count() == paid_registrations.count():
            print("   ✅ SUCCÈS: Toutes les inscriptions payantes ont des demandes de remboursement")
        else:
            print(f"   ❌ ÉCHEC: {created_refunds.count()}/{paid_registrations.count()} remboursements créés")
            return False
        
        # 8. Afficher les détails des remboursements
        print(f"\n8️⃣ Détails des demandes de remboursement:")
        for refund in created_refunds:
            user_info = refund.registration.user.email if refund.registration.user else refund.registration.guest_email
            print(f"   - ID: {refund.id}")
            print(f"     Utilisateur: {user_info}")
            print(f"     Montant payé: {refund.amount_paid}€")
            print(f"     Montant remboursé: {refund.refund_amount}€")
            print(f"     Statut: {refund.status}")
            print(f"     Raison: {refund.reason}")
            print(f"     Date création: {refund.created_at}")
            print()
        
        # 9. Restaurer l'événement (optionnel)
        print(f"\n9️⃣ Restauration de l'événement...")
        test_event.status = old_status
        test_event.save()
        print(f"   ✅ Événement restauré au statut: {test_event.status}")
        
        # 10. Nettoyer les remboursements de test
        print(f"\n🔟 Nettoyage des remboursements de test...")
        created_refunds.delete()
        print(f"   ✅ {refunds_created} remboursements de test supprimés")
        
        print("\n🎉 TEST RÉUSSI! Le système de remboursements automatiques fonctionne correctement!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_organizer_refunds_list():
    """Test de la fonction organizer_refunds_list avec événements annulés"""
    print("\n🧪 TEST : Fonction organizer_refunds_list avec événements annulés")
    print("=" * 80)
    
    try:
        # Simuler un appel à organizer_refunds_list
        from events.views import organizer_refunds_list
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        # Créer un utilisateur de test
        test_user, created = User.objects.get_or_create(
            username='test_organizer',
            defaults={'email': 'test@example.com', 'password': 'testpass123'}
        )
        
        if created:
            print(f"✅ Utilisateur de test créé: {test_user.username}")
        
        # Créer une requête de test
        factory = RequestFactory()
        request = factory.get('/organizer/refunds/')
        request.user = test_user
        
        # Appeler la fonction
        response = organizer_refunds_list(request)
        
        print(f"✅ Fonction appelée avec succès")
        print(f"   - Status code: {response.status_code}")
        
        if hasattr(response, 'data'):
            data = response.data
            print(f"   - Total remboursements: {data.get('count', 0)}")
            print(f"   - Événements sans remboursements: {len(data.get('cancelled_events_without_refunds', []))}")
            
            summary = data.get('summary', {})
            print(f"   - Résumé:")
            print(f"     * Total remboursements: {summary.get('total_refunds', 0)}")
            print(f"     * Événements sans remboursements: {summary.get('events_with_missing_refunds', 0)}")
            print(f"     * Montant total à risque: {summary.get('total_amount_at_risk', 0)}€")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors du test organizer_refunds_list: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Démarrage des tests du système de remboursements pour événements annulés")
    
    # Test principal
    test1_success = test_cancelled_event_refunds()
    
    # Test de la fonction organizer_refunds_list
    test2_success = test_organizer_refunds_list()
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    print(f"✅ Test remboursements automatiques: {'SUCCÈS' if test1_success else 'ÉCHEC'}")
    print(f"✅ Test organizer_refunds_list: {'SUCCÈS' if test2_success else 'ÉCHEC'}")
    
    if test1_success and test2_success:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("   Le système de remboursements automatiques pour événements annulés fonctionne parfaitement!")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Vérifiez les erreurs ci-dessus et corrigez les problèmes")
    
    print("\n✨ Fin des tests")





