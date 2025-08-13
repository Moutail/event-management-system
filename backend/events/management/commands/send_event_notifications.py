from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from events.models import Event, EventRegistration, NotificationLog


class Command(BaseCommand):
    help = "Envoie les rappels et notifications d'événements (J-1, jour J, updates, remerciements)."

    def handle(self, *args, **options):
        now = timezone.now()
        self.send_reminder_1d(now)
        self.send_reminder_day(now)
        self.send_thank_you(now)
        self.stdout.write(self.style.SUCCESS("Notifications traitées."))

    def _send_email(self, subject: str, to_email: str, template_html: str, template_txt: str, context: dict):
        text_body = render_to_string(template_txt, context)
        html_body = render_to_string(template_html, context)
        msg = EmailMultiAlternatives(subject, text_body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [to_email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=True)

    def send_reminder_1d(self, now):
        # Rappel J-1: événements qui commencent entre 24h et 48h
        start_min = now + timezone.timedelta(hours=24)
        start_max = now + timezone.timedelta(hours=48)
        events = Event.objects.filter(start_date__gte=start_min, start_date__lt=start_max, status='published')
        for event in events:
            regs = EventRegistration.objects.filter(event=event, status__in=['pending', 'confirmed'])
            for reg in regs:
                if NotificationLog.objects.filter(event=event, registration=reg, type='reminder_1d').exists():
                    continue
                ctx = {'user': reg.user, 'event': event}
                self._send_email(f"Rappel: {event.title} demain", reg.user.email,
                                 'emails/reminder_1d.html', 'emails/reminder_1d.txt', ctx)
                NotificationLog.objects.create(event=event, registration=reg, type='reminder_1d')

    def send_reminder_day(self, now):
        # Rappel jour J: événements qui commencent dans les prochaines 6 heures
        start_min = now
        start_max = now + timezone.timedelta(hours=6)
        events = Event.objects.filter(start_date__gte=start_min, start_date__lt=start_max, status='published')
        for event in events:
            regs = EventRegistration.objects.filter(event=event, status__in=['pending', 'confirmed'])
            for reg in regs:
                if NotificationLog.objects.filter(event=event, registration=reg, type='reminder_day').exists():
                    continue
                ctx = {'user': reg.user, 'event': event}
                self._send_email(f"C'est aujourd'hui: {event.title}", reg.user.email,
                                 'emails/reminder_day.html', 'emails/reminder_day.txt', ctx)
                NotificationLog.objects.create(event=event, registration=reg, type='reminder_day')

    def send_thank_you(self, now):
        # Merci post-événement: événements terminés dans les dernières 12h
        end_min = now - timezone.timedelta(hours=12)
        end_max = now
        events = Event.objects.filter(end_date__gte=end_min, end_date__lt=end_max, status__in=['published', 'completed'])
        for event in events:
            regs = EventRegistration.objects.filter(event=event, status__in=['confirmed', 'attended'])
            for reg in regs:
                if NotificationLog.objects.filter(event=event, registration=reg, type='thank_you').exists():
                    continue
                ctx = {'user': reg.user, 'event': event}
                self._send_email(f"Merci pour votre participation - {event.title}", reg.user.email,
                                 'emails/thank_you.html', 'emails/thank_you.txt', ctx)
                NotificationLog.objects.create(event=event, registration=reg, type='thank_you')

