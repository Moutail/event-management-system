#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import RefundRequest, EventRegistration, RefundPolicy
from django.utils import timezone

print("=== CRÉATION DES DEMANDES DE REMBOURSEMENT MANQUANTES ===")

# Récupérer toutes les inscriptions annulées payées sans demande de remboursement
cancelled_paid = EventRegistration.objects.filter(
    status='cancelled',
    payment_status='paid',
    price_paid__gt=0
).exclude(
    refund_request__isnull=False  # Exclure celles qui ont déjà une demande
)

print(f"📊 Inscriptions annulées payées sans demande de remboursement: {cancelled_paid.count()}")

created_count = 0

for registration in cancelled_paid:
    try:
        event = registration.event
        
        # Obtenir ou créer la politique de remboursement
        try:
            policy = event.refund_policy
        except RefundPolicy.DoesNotExist:
            policy = RefundPolicy.objects.create(
                event=event,
                mode='mixed',  # Manuel puis automatique après 24h
                auto_refund_delay_hours=24,
                refund_percentage_immediate=100,
                refund_percentage_after_delay=100,
                cutoff_hours_before_event=24,
                allow_partial_refunds=True,
                require_reason=False,
                notify_organizer_on_cancellation=True
            )
            print(f"  📋 Politique créée pour {event.title}")
        
        # Calculer les montants et dates
        refund_percentage = policy.get_refund_percentage(0)
        refund_amount = (registration.price_paid * refund_percentage) / 100
        
        now = timezone.now()
        auto_process_at = None
        if policy.mode in ['auto', 'mixed']:
            auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
        
        expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
        
        # Créer la demande de remboursement
        refund_request = RefundRequest.objects.create(
            registration=registration,
            reason='Annulation par l\'utilisateur (récupération automatique)',
            amount_paid=registration.price_paid,
            refund_percentage=refund_percentage,
            refund_amount=refund_amount,
            auto_process_at=auto_process_at,
            expires_at=expires_at
        )
        
        print(f"  ✅ Demande créée: ID={refund_request.id}")
        print(f"     User: {registration.user.email}")
        print(f"     Event: {event.title}")
        print(f"     Amount: {refund_amount}€")
        print()
        
        created_count += 1
        
    except Exception as e:
        print(f"  ❌ Erreur pour inscription {registration.id}: {e}")
        import traceback
        traceback.print_exc()
        print()

print(f"🎉 TERMINÉ: {created_count} demandes de remboursement créées !")
print("\nMaintenant retournez sur l'interface 'Gérer les remboursements' - vous devriez voir toutes les demandes !")
print("=== FIN ===")






