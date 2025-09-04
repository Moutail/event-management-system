#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import EventRegistration, RefundRequest

print("=== DEBUG ANNULATION RÉCENTE ===")

# Vérifier l'inscription 64 qui vient d'être annulée
reg = EventRegistration.objects.filter(id=64).first()
if reg:
    print(f"📋 Registration 64:")
    print(f"   Status: {reg.status}")
    print(f"   Payment status: {reg.payment_status}")
    print(f"   Price paid: {reg.price_paid}€")
    print(f"   Event: {reg.event.title}")
    print(f"   User: {reg.user.email}")
    
    # Vérifier s'il y a une demande de remboursement
    try:
        refund_req = reg.refund_request
        print(f"   ✅ Has refund request: ID={refund_req.id}, Status={refund_req.status}")
    except:
        print(f"   ❌ No refund request found")
        
        # Si pas de demande, créons-en une manuellement
        if reg.payment_status == 'paid' and reg.price_paid > 0:
            print(f"   🔧 Creating refund request manually...")
            try:
                from events.models import RefundPolicy
                from django.utils import timezone
                
                # Créer politique si nécessaire
                try:
                    policy = reg.event.refund_policy
                except RefundPolicy.DoesNotExist:
                    policy = RefundPolicy.objects.create(
                        event=reg.event,
                        mode='mixed',
                        auto_refund_delay_hours=24,
                        refund_percentage_immediate=100
                    )
                
                # Créer demande de remboursement
                refund_request = RefundRequest.objects.create(
                    registration=reg,
                    reason='Annulation automatique (récupération debug)',
                    amount_paid=reg.price_paid,
                    refund_percentage=100,
                    refund_amount=reg.price_paid,
                    auto_process_at=timezone.now() + timezone.timedelta(hours=24),
                    expires_at=reg.event.start_date - timezone.timedelta(hours=24)
                )
                
                print(f"   ✅ Refund request created: ID={refund_request.id}")
                
            except Exception as e:
                print(f"   ❌ Error creating refund request: {e}")
                import traceback
                traceback.print_exc()
else:
    print("❌ Registration 64 not found")

print("\n=== TOUTES LES DEMANDES DE REMBOURSEMENT ===")
all_refunds = RefundRequest.objects.all().order_by('-created_at')
for refund in all_refunds:
    print(f"ID {refund.id}: {refund.registration.user.email} - {refund.registration.event.title} - {refund.refund_amount}€ ({refund.status})")

print("=== FIN DEBUG ===")






