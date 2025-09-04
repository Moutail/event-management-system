#!/usr/bin/env python
"""
🧪 TEST : API des remboursements pour vérifier qu'elle fonctionne
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, EventRegistration, RefundRequest, RefundPolicy
from events.views import EventViewSet
from django.utils import timezone
from datetime import timedelta

def test_automatic_refund_creation():
    """Test de la création automatique des remboursements lors de l'annulation d'un événement"""
    print("🚀 Test de création automatique des remboursements")
    
    try:
        # Créer un utilisateur test
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_organizer',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Organizer'
            }
        )
        
        # Créer un événement payant
        event = Event.objects.create(
            title='TEST ÉVÉNEMENT PAYANT',
            description='Test pour vérifier la création automatique des remboursements',
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=7, hours=2),
            location='Test Location',
            price=50.00,  # Événement payant
            organizer=user,
            status='published'
        )
        
        # Créer des inscriptions payantes
        registration1 = EventRegistration.objects.create(
            event=event,
            user=user,
            status='confirmed',
            payment_status='paid',
            price_paid=50.00
        )
        
        # Créer une inscription pour un invité
        registration2 = EventRegistration.objects.create(
            event=event,
            user=None,
            guest_full_name='Invité Test',
            guest_email='invite@example.com',
            status='confirmed',
            payment_status='paid',
            price_paid=50.00
        )
        
        print(f"✅ Événement créé: {event.title} (ID: {event.id})")
        print(f"✅ Inscriptions créées: {EventRegistration.objects.filter(event=event).count()}")
        
        # Simuler l'annulation de l'événement
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post(f'/api/events/{event.id}/cancel/', {
            'reason': 'Test de création automatique des remboursements'
        })
        
        print(f"🔍 Réponse de l'annulation: {response.status_code}")
        if response.status_code == 200:
            print(f"🔍 Contenu de la réponse: {response.data}")
            
            # Vérifier que les remboursements ont été créés
            refunds = RefundRequest.objects.filter(registration__event=event)
            print(f"🔍 Remboursements créés: {refunds.count()}")
            
            for refund in refunds:
                print(f"  - ID: {refund.id}, Montant: {refund.refund_amount}€, Raison: {refund.reason}")
            
            # Vérifier que l'événement est annulé
            event.refresh_from_db()
            print(f"🔍 Statut de l'événement après annulation: {event.status}")
            
        else:
            print(f"❌ Erreur lors de l'annulation: {response.data}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_automatic_refund_creation()
