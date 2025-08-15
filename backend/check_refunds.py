#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import RefundRequest, EventRegistration

print("=== VÉRIFICATION DES DEMANDES DE REMBOURSEMENT ===")

# Compter les demandes de remboursement
refund_count = RefundRequest.objects.count()
print(f"📊 Total demandes de remboursement: {refund_count}")

if refund_count > 0:
    print("\n📋 Liste des demandes:")
    for r in RefundRequest.objects.all():
        print(f"  - ID: {r.id}")
        print(f"    User: {r.registration.user.email}")
        print(f"    Event: {r.registration.event.title}")
        print(f"    Status: {r.status}")
        print(f"    Amount: {r.refund_amount}€")
        print(f"    Created: {r.created_at}")
        print()

# Compter les inscriptions annulées avec paiement
cancelled_paid = EventRegistration.objects.filter(
    status='cancelled',
    payment_status='paid',
    price_paid__gt=0
)

print(f"\n💰 Inscriptions annulées ET payées: {cancelled_paid.count()}")
if cancelled_paid.count() > 0:
    print("📋 Liste des inscriptions annulées payées:")
    for reg in cancelled_paid:
        print(f"  - ID: {reg.id}")
        print(f"    User: {reg.user.email}")
        print(f"    Event: {reg.event.title}")
        print(f"    Amount paid: {reg.price_paid}€")
        print(f"    Has refund request: {hasattr(reg, 'refund_request')}")
        print()

print("=== FIN VÉRIFICATION ===")



