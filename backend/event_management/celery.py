import os
from celery import Celery

# Configuration de Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')

app = Celery('event_management')

# Configuration Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découverte automatique des tâches
app.autodiscover_tasks()

# Configuration du broker (utilise les paramètres de settings.py)
# Les paramètres sont chargés depuis settings.py via config_from_object

# Configuration des tâches périodiques pour les rappels automatiques
app.conf.beat_schedule = {
    'check-scheduled-reminders': {
        'task': 'events.tasks.check_scheduled_reminders',
        'schedule': 60.0,  # Vérifier toutes les minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

