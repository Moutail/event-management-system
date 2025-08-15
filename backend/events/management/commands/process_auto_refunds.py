from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from events.models import RefundRequest
import stripe


class Command(BaseCommand):
    help = "Traite automatiquement les demandes de remboursement en attente"

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Récupérer les demandes à traiter automatiquement
        pending_refunds = RefundRequest.objects.filter(
            status='pending',
            auto_process_at__lte=now
        )
        
        processed_count = 0
        failed_count = 0
        
        for refund_request in pending_refunds:
            try:
                if self._process_refund(refund_request):
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Remboursement traité: {refund_request}")
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ Échec remboursement: {refund_request}")
                    )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur remboursement {refund_request}: {e}")
                )
        
        # Marquer les demandes expirées
        expired_refunds = RefundRequest.objects.filter(
            status='pending',
            expires_at__lt=now
        )
        
        expired_count = expired_refunds.count()
        expired_refunds.update(status='expired')
        
        # Résumé
        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Résumé du traitement automatique:"
                f"\n• Remboursements traités: {processed_count}"
                f"\n• Échecs: {failed_count}"
                f"\n• Expirés: {expired_count}"
            )
        )

    def _process_refund(self, refund_request):
        """Traite un remboursement individuel"""
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            print(f"❌ Stripe non configuré pour {refund_request}")
            return False
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            # Exécuter le remboursement Stripe
            refund = stripe.Refund.create(
                payment_intent=refund_request.registration.payment_reference,
                amount=int(refund_request.refund_amount * 100),  # Centimes
                reason='requested_by_customer'
            )
            
            # Mettre à jour la demande
            refund_request.status = 'processed'
            refund_request.processed_at = timezone.now()
            refund_request.stripe_refund_id = refund.id
            refund_request.save()
            
            # Mettre à jour l'inscription
            registration = refund_request.registration
            registration.payment_status = 'refunded'
            registration.status = 'cancelled'
            registration.save()
            
            # Mettre à jour les compteurs
            self._update_counters(registration)
            
            # Envoyer email de confirmation
            self._send_confirmation_email(refund_request)
            
            return True
            
        except stripe.error.StripeError as e:
            print(f"❌ Erreur Stripe pour {refund_request}: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur générale pour {refund_request}: {e}")
            return False

    def _update_counters(self, registration):
        """Met à jour les compteurs après remboursement"""
        event = registration.event
        
        if registration.status in ['confirmed', 'attended']:
            event.current_registrations = max(0, (event.current_registrations or 0) - 1)
            event.save(update_fields=['current_registrations'])
            
            if registration.ticket_type:
                tt = registration.ticket_type
                tt.sold_count = max(0, (tt.sold_count or 0) - 1)
                tt.save(update_fields=['sold_count'])

    def _send_confirmation_email(self, refund_request):
        """Envoie l'email de confirmation de remboursement"""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            
            registration = refund_request.registration
            event = registration.event
            
            subject = f"Remboursement traité automatiquement - {event.title}"
            context = {
                'user': registration.user,
                'event': event,
                'refund_request': refund_request,
                'refund_amount': refund_request.refund_amount
            }
            
            text_body = render_to_string('emails/refund_confirmation.txt', context)
            html_body = render_to_string('emails/refund_confirmation.html', context)
            
            msg = EmailMultiAlternatives(
                subject, 
                text_body, 
                settings.DEFAULT_FROM_EMAIL, 
                [registration.user.email]
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            
            print(f"📧 Email envoyé à {registration.user.email}")
            
        except Exception as e:
            print(f"❌ Erreur envoi email pour {refund_request}: {e}")



