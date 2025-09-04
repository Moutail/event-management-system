#!/usr/bin/env python
"""
🔄 SCRIPT DE TRAITEMENT MANUEL DES RAPPELS AUTOMATIQUES
Alternative à Celery pour traiter les rappels programmés
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.utils import timezone
from events.models import CustomReminder
from events.tasks import send_reminder_task

def process_scheduled_reminders():
    """Traiter les rappels programmés"""
    try:
        print(f"🔍 DEBUG: ===== TRAITEMENT MANUEL DES RAPPELS =====")
        now = timezone.now()
        print(f"🔍 DEBUG: Heure actuelle: {now}")

        # Récupérer les rappels programmés qui sont en retard
        time_threshold = now + timedelta(minutes=5)  # Marge de 5 minutes
        reminders_to_send = CustomReminder.objects.filter(
            status='scheduled',
            scheduled_at__lte=time_threshold
        ).order_by('scheduled_at')

        print(f"🔍 DEBUG: Rappels à traiter: {reminders_to_send.count()}")

        sent_count = 0
        for reminder in reminders_to_send:
            try:
                print(f"🔍 DEBUG: Traitement du rappel {reminder.id}: {reminder.title}")
                print(f"🔍 DEBUG: Heure programmée: {reminder.scheduled_at}")
                print(f"🔍 DEBUG: Minutes de retard: {(now - reminder.scheduled_at).total_seconds() / 60:.1f}")

                recipients = reminder.get_recipients()
                if not recipients.exists():
                    print(f"🔍 DEBUG: ⚠️ Aucun destinataire pour le rappel {reminder.id}")
                    reminder.status = 'failed'
                    reminder.save()
                    continue

                print(f"🔍 DEBUG: Destinataires trouvés: {recipients.count()}")
                
                # Appeler directement la fonction d'envoi
                result = send_reminder_task(reminder.id)
                print(f"🔍 DEBUG: ✅ Rappel {reminder.id} traité: {result}")
                sent_count += 1

            except Exception as e:
                print(f"🔍 DEBUG: ❌ Erreur traitement rappel {reminder.id}: {e}")
                reminder.status = 'failed'
                reminder.save()

        print(f"🔍 DEBUG: ==========================================")
        print(f"🔍 DEBUG: Rappels traités: {sent_count}/{reminders_to_send.count()}")
        return f"Traité {reminders_to_send.count()} rappels, envoyé {sent_count}"

    except Exception as e:
        print(f"🔍 DEBUG: ❌ Erreur traitement: {e}")
        import traceback
        traceback.print_exc()
        return f"Erreur: {str(e)}"

def run_continuous_monitoring():
    """Lancer la surveillance continue"""
    print("🚀 DÉMARRAGE DU MONITORING DES RAPPELS AUTOMATIQUES")
    print("=" * 60)
    print("💡 Ce script vérifie les rappels programmés toutes les 30 secondes")
    print("💡 Pour arrêter: Ctrl+C")
    print("=" * 60)
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Vérification des rappels...")
            result = process_scheduled_reminders()
            print(f"📊 Résultat: {result}")
            
            # Attendre 30 secondes avant la prochaine vérification
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du monitoring demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur dans le monitoring: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Mode une seule fois
        print("🔄 TRAITEMENT UNIQUE DES RAPPELS")
        result = process_scheduled_reminders()
        print(f"📊 Résultat: {result}")
    else:
        # Mode continu
        run_continuous_monitoring()
