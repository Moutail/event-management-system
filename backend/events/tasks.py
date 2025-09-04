from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_reminder_task(self, reminder_id):
    """
    Tâche Celery pour envoyer un rappel automatiquement
    """
    try:
        from .models import CustomReminder
        
        print(f"🔍 DEBUG: ===== TÂCHE CELERY DÉBUT =====")
        print(f"🔍 DEBUG: Reminder ID: {reminder_id}")
        print(f"🔍 DEBUG: Task ID: {self.request.id}")
        
        # Récupérer le rappel
        try:
            reminder = CustomReminder.objects.get(id=reminder_id)
            print(f"🔍 DEBUG: Rappel trouvé: {reminder}")
        except CustomReminder.DoesNotExist:
            print(f"🔍 DEBUG: ❌ Rappel {reminder_id} non trouvé")
            return {'status': 'error', 'message': 'Rappel non trouvé'}
        
        # Vérifier si le rappel peut être envoyé
        if reminder.status != 'scheduled':
            print(f"🔍 DEBUG: ❌ Rappel pas en statut 'scheduled': {reminder.status}")
            return {'status': 'error', 'message': f'Rappel pas en statut scheduled: {reminder.status}'}
        
        # Vérifier si l'heure est arrivée
        now = timezone.now()
        if reminder.scheduled_at > now:
            print(f"🔍 DEBUG: ❌ Heure pas encore arrivée: {reminder.scheduled_at} > {now}")
            return {'status': 'error', 'message': 'Heure pas encore arrivée'}
        
        print(f"🔍 DEBUG: ✅ Heure arrivée, envoi du rappel...")
        
        # Récupérer les destinataires
        recipients = reminder.get_recipients()
        print(f"🔍 DEBUG: Nombre de destinataires: {recipients.count()}")
        
        if not recipients.exists():
            print(f"🔍 DEBUG: ❌ Aucun destinataire trouvé")
            reminder.status = 'failed'
            reminder.save()
            return {'status': 'error', 'message': 'Aucun destinataire trouvé'}
        
        # Initialiser les statistiques
        statistics = {
            'total_recipients': recipients.count(),
            'emails_sent': 0,
            'sms_sent': 0,
            'emails_failed': 0,
            'sms_failed': 0
        }
        
        # Envoyer à chaque destinataire
        for registration in recipients:
            print(f"🔍 DEBUG: ===== TRAITEMENT DESTINATAIRE =====")
            print(f"🔍 DEBUG: Registration ID: {registration.id}")
            print(f"🔍 DEBUG: Registration Type: {'User' if registration.user else 'Guest'}")
            
            # Déterminer le nom et l'email selon le type d'inscription
            if registration.user:
                # Inscription d'utilisateur connecté
                recipient_name = registration.user.get_full_name() or registration.user.username
                recipient_email = registration.user.email
                recipient_phone = getattr(registration.user.profile, 'phone', '') if hasattr(registration.user, 'profile') else ''
                print(f"🔍 DEBUG: User - Name: {recipient_name}, Email: {recipient_email}, Phone: {recipient_phone}")
            else:
                # Inscription d'invité
                recipient_name = registration.guest_full_name or "Invité"
                recipient_email = registration.guest_email or ""
                recipient_phone = registration.guest_phone or ""
                print(f"🔍 DEBUG: Guest - Name: {recipient_name}, Email: {recipient_email}, Phone: {recipient_phone}")
            
            # Envoyer email si activé
            if reminder.send_email and recipient_email:
                print(f"🔍 DEBUG: 📧 ENVOI EMAIL à {recipient_email}")
                email_sent = send_reminder_email_task(reminder, registration)
                if email_sent:
                    statistics['emails_sent'] += 1
                    print(f"🔍 DEBUG: ✅ Email envoyé avec succès")
                else:
                    statistics['emails_failed'] += 1
                    print(f"🔍 DEBUG: ❌ Échec envoi email")
            
            # Envoyer SMS si activé
            if reminder.send_sms and recipient_phone:
                print(f"🔍 DEBUG: 📱 ENVOI SMS à {recipient_phone}")
                sms_sent = send_reminder_sms_task(reminder, registration)
                if sms_sent:
                    statistics['sms_sent'] += 1
                    print(f"🔍 DEBUG: ✅ SMS envoyé avec succès")
                else:
                    statistics['sms_failed'] += 1
                    print(f"🔍 DEBUG: ❌ Échec envoi SMS")
        
        # Mettre à jour le rappel
        reminder.status = 'sent'
        reminder.sent_at = timezone.now()
        reminder.emails_sent = statistics['emails_sent']
        reminder.sms_sent = statistics['sms_sent']
        reminder.emails_failed = statistics['emails_failed']
        reminder.sms_failed = statistics['sms_failed']
        reminder.save()
        
        print(f"🔍 DEBUG: Statistiques finales: {statistics}")
        print(f"🔍 DEBUG: ===== TÂCHE CELERY FIN =====")
        
        return {
            'status': 'success',
            'message': 'Rappel envoyé avec succès',
            'statistics': statistics
        }
        
    except Exception as e:
        print(f"🔍 DEBUG: ❌ Erreur dans la tâche Celery: {e}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        
        # Marquer le rappel comme échoué
        try:
            reminder = CustomReminder.objects.get(id=reminder_id)
            reminder.status = 'failed'
            reminder.save()
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}

def send_reminder_email_task(reminder, registration):
    """Envoyer le rappel par email"""
    try:
        # Déterminer l'email et le nom du destinataire selon le type d'inscription
        if registration.user:
            # Inscription d'utilisateur connecté
            recipient_email = registration.user.email
            recipient_name = registration.user.get_full_name() or registration.user.username
        else:
            # Inscription d'invité
            recipient_email = registration.guest_email
            recipient_name = registration.guest_full_name or "Invité"
        
        if not recipient_email:
            print(f"🔍 DEBUG: ❌ Aucun email disponible pour {recipient_name}")
            return False
        
        # Créer le sujet et le message
        subject = f"[{reminder.event.title}] {reminder.title}"
        message = f"""
Bonjour {recipient_name},

{reminder.message}

Détails de l'événement :
- Titre : {reminder.event.title}
- Date : {reminder.event.start_date.strftime('%d/%m/%Y à %H:%M')}
- Lieu : {reminder.event.location}

Cordialement,
L'équipe {reminder.event.title}
        """
        
        # Envoyer l'email
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[recipient_email],
            fail_silently=False
        )
        
        print(f"🔍 DEBUG: ✅ Email envoyé avec succès à {recipient_email}")
        return True
        
    except Exception as e:
        print(f"🔍 DEBUG: ❌ Erreur envoi email: {e}")
        return False

def send_reminder_sms_task(reminder, registration):
    """Envoyer le rappel par SMS"""
    try:
        # Déterminer le téléphone et le nom du destinataire selon le type d'inscription
        if registration.user:
            # Inscription d'utilisateur connecté
            recipient_phone = getattr(registration.user.profile, 'phone', '') if hasattr(registration.user, 'profile') else ''
            recipient_name = registration.user.get_full_name() or registration.user.username
        else:
            # Inscription d'invité
            recipient_phone = registration.guest_phone
            recipient_name = registration.guest_full_name or "Invité"
        
        if not recipient_phone:
            print(f"🔍 DEBUG: ❌ Aucun téléphone disponible pour {recipient_name}")
            return False
        
        # Créer le message SMS
        message = f"{reminder.title}\n\n{reminder.message}\n\nÉvénement: {reminder.event.title}\nDate: {reminder.event.start_date.strftime('%d/%m/%Y à %H:%M')}"
        
        # Vérifier si Twilio est activé
        if not getattr(settings, 'TWILIO_ENABLED', False):
            print(f"🔍 DEBUG: ⚠️ Twilio désactivé - Simulation SMS")
            return True
        
        # Envoi SMS réel avec Twilio
        try:
            from twilio.rest import Client
            
            client = Client(
                getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
                getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            )
            
            twilio_message = client.messages.create(
                body=message,
                from_=getattr(settings, 'TWILIO_FROM_NUMBER', ''),
                to=recipient_phone
            )
            
            print(f"🔍 DEBUG: ✅ SMS envoyé avec succès via Twilio!")
            print(f"🔍 DEBUG: Message SID: {twilio_message.sid}")
            return True
            
        except ImportError:
            print(f"🔍 DEBUG: ❌ Module twilio non installé - Simulation SMS")
            return True
            
        except Exception as twilio_error:
            print(f"🔍 DEBUG: ❌ Erreur Twilio: {twilio_error}")
            return False
        
    except Exception as e:
        print(f"🔍 DEBUG: ❌ Erreur envoi SMS: {e}")
        return False

@shared_task
def check_scheduled_reminders():
    """
    Tâche périodique pour vérifier les rappels programmés
    """
    try:
        from .models import CustomReminder
        from django.utils import timezone
        
        print(f"🔍 DEBUG: ===== VÉRIFICATION RAPPELS PROGRAMMÉS =====")
        
        now = timezone.now()
        print(f"🔍 DEBUG: Heure actuelle: {now}")
        
        # Récupérer les rappels programmés dont l'heure est arrivée
        # On ajoute une marge de 5 minutes pour éviter les problèmes de timing
        from datetime import timedelta
        time_threshold = now + timedelta(minutes=5)
        
        reminders_to_send = CustomReminder.objects.filter(
            status='scheduled',
            scheduled_at__lte=time_threshold
        ).order_by('scheduled_at')
        
        print(f"🔍 DEBUG: Rappels à envoyer: {reminders_to_send.count()}")
        
        sent_count = 0
        for reminder in reminders_to_send:
            try:
                print(f"🔍 DEBUG: Traitement du rappel {reminder.id}: {reminder.title}")
                print(f"🔍 DEBUG: Heure programmée: {reminder.scheduled_at}")
                
                # Vérifier si le rappel a des destinataires
                recipients = reminder.get_recipients()
                if not recipients.exists():
                    print(f"🔍 DEBUG: ⚠️ Aucun destinataire pour le rappel {reminder.id}")
                    reminder.status = 'failed'
                    reminder.save()
                    continue
                
                # Envoyer le rappel directement (pas besoin de delay car l'heure est déjà arrivée)
                result = send_reminder_task(reminder.id)
                print(f"🔍 DEBUG: ✅ Rappel {reminder.id} envoyé: {result}")
                sent_count += 1
                
            except Exception as e:
                print(f"🔍 DEBUG: ❌ Erreur envoi rappel {reminder.id}: {e}")
                reminder.status = 'failed'
                reminder.save()
        
        print(f"🔍 DEBUG: ==========================================")
        print(f"🔍 DEBUG: Rappels envoyés: {sent_count}/{reminders_to_send.count()}")
        
        return f"Vérifié {reminders_to_send.count()} rappels, envoyé {sent_count}"
        
    except Exception as e:
        print(f"🔍 DEBUG: ❌ Erreur vérification rappels: {e}")
        import traceback
        traceback.print_exc()
        return f"Erreur: {str(e)}"

