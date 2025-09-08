from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import logging

from events.models import Event, EventRegistration, NotificationLog

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Envoie les rappels et notifications d'événements (pour cron externe)"

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f"🕐 Exécution des notifications à {now}")
        
        try:
            # Envoyer les rappels
            self.send_reminder_1d(now)
            self.send_reminder_1h(now)
            self.send_reminder_day(now)
            self.send_thank_you(now)
            self.process_auto_refunds(now)
            
            self.stdout.write(self.style.SUCCESS("✅ Notifications traitées avec succès"))
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi des notifications: {e}")
            self.stdout.write(self.style.ERROR(f"❌ Erreur: {e}"))

    def _send_email(self, subject: str, to_email: str, template_html: str, template_txt: str, context: dict):
        """Envoie un email avec template HTML et texte"""
        try:
            text_body = render_to_string(template_txt, context)
            html_body = render_to_string(template_html, context)
            
            msg = EmailMultiAlternatives(
                subject, 
                text_body, 
                getattr(settings, 'DEFAULT_FROM_EMAIL', None), 
                [to_email]
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)
            
            logger.info(f"📧 Email envoyé à {to_email}: {subject}")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi email à {to_email}: {e}")

    def send_reminder_1d(self, now):
        """Rappel J-1: événements qui commencent dans exactement 24h (±30min)"""
        from datetime import timedelta
        
        target_time = now + timedelta(hours=24)
        start_time = target_time - timedelta(minutes=30)
        end_time = target_time + timedelta(minutes=30)
        
        events = Event.objects.filter(
            start_date__gte=start_time,
            start_date__lte=end_time,
            status='published'
        )
        
        for event in events:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            )
            
            for registration in registrations:
                context = {
                    'event': event,
                    'registration': registration,
                    'user': registration.user
                }
                
                self._send_email(
                    f"Rappel: {event.title} dans 24h",
                    registration.user.email,
                    'emails/reminder_1d.html',
                    'emails/reminder_1d.txt',
                    context
                )
                
                # Log de la notification
                NotificationLog.objects.create(
                    event=event,
                    user=registration.user,
                    notification_type='reminder_1d',
                    status='sent',
                    message=f"Rappel J-1 envoyé pour {event.title}"
                )

    def send_reminder_1h(self, now):
        """Rappel 1h: événements qui commencent dans exactement 1h (±15min)"""
        from datetime import timedelta
        
        target_time = now + timedelta(hours=1)
        start_time = target_time - timedelta(minutes=15)
        end_time = target_time + timedelta(minutes=15)
        
        events = Event.objects.filter(
            start_date__gte=start_time,
            start_date__lte=end_time,
            status='published'
        )
        
        for event in events:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            )
            
            for registration in registrations:
                context = {
                    'event': event,
                    'registration': registration,
                    'user': registration.user
                }
                
                self._send_email(
                    f"Dernier rappel: {event.title} dans 1h",
                    registration.user.email,
                    'emails/reminder_1h.html',
                    'emails/reminder_1h.txt',
                    context
                )
                
                # Log de la notification
                NotificationLog.objects.create(
                    event=event,
                    user=registration.user,
                    notification_type='reminder_1h',
                    status='sent',
                    message=f"Rappel 1h envoyé pour {event.title}"
                )

    def send_reminder_day(self, now):
        """Rappel jour J: événements qui commencent aujourd'hui"""
        from datetime import timedelta
        
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        events = Event.objects.filter(
            start_date__gte=start_of_day,
            start_date__lt=end_of_day,
            status='published'
        )
        
        for event in events:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            )
            
            for registration in registrations:
                context = {
                    'event': event,
                    'registration': registration,
                    'user': registration.user
                }
                
                self._send_email(
                    f"🎉 C'est aujourd'hui: {event.title}",
                    registration.user.email,
                    'emails/reminder_day.html',
                    'emails/reminder_day.txt',
                    context
                )
                
                # Log de la notification
                NotificationLog.objects.create(
                    event=event,
                    user=registration.user,
                    notification_type='reminder_day',
                    status='sent',
                    message=f"Rappel jour J envoyé pour {event.title}"
                )

    def send_thank_you(self, now):
        """Remerciement: événements qui se sont terminés il y a 12h"""
        from datetime import timedelta
        
        target_time = now - timedelta(hours=12)
        start_time = target_time - timedelta(hours=1)
        end_time = target_time + timedelta(hours=1)
        
        events = Event.objects.filter(
            end_date__gte=start_time,
            end_date__lte=end_time,
            status='published'
        )
        
        for event in events:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            )
            
            for registration in registrations:
                context = {
                    'event': event,
                    'registration': registration,
                    'user': registration.user
                }
                
                self._send_email(
                    f"Merci d'avoir participé à {event.title}",
                    registration.user.email,
                    'emails/thank_you.html',
                    'emails/thank_you.txt',
                    context
                )
                
                # Log de la notification
                NotificationLog.objects.create(
                    event=event,
                    user=registration.user,
                    notification_type='thank_you',
                    status='sent',
                    message=f"Remerciement envoyé pour {event.title}"
                )

    def process_auto_refunds(self, now):
        """Traite les remboursements automatiques"""
        from datetime import timedelta
        
        # Événements annulés il y a plus de 24h
        target_time = now - timedelta(hours=24)
        
        events = Event.objects.filter(
            status='cancelled',
            updated_at__lte=target_time
        )
        
        for event in events:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed',
                refund_status__isnull=True
            )
            
            for registration in registrations:
                # Traiter le remboursement automatique
                try:
                    # Logique de remboursement ici
                    registration.refund_status = 'approved'
                    registration.save()
                    
                    # Envoyer email de remboursement
                    context = {
                        'event': event,
                        'registration': registration,
                        'user': registration.user
                    }
                    
                    self._send_email(
                        f"Remboursement approuvé pour {event.title}",
                        registration.user.email,
                        'emails/refund_approved.html',
                        'emails/refund_approved.txt',
                        context
                    )
                    
                    # Log de la notification
                    NotificationLog.objects.create(
                        event=event,
                        user=registration.user,
                        notification_type='refund_approved',
                        status='sent',
                        message=f"Remboursement approuvé pour {event.title}"
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Erreur remboursement pour {registration.id}: {e}")
