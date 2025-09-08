"""
Vues pour les tâches cron externes
Permet d'appeler les notifications via des requêtes HTTP
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def trigger_notifications(request):
    """
    Déclenche l'envoi des notifications via une requête HTTP
    Utilisé par les services cron externes
    """
    try:
        # Vérifier l'autorisation (optionnel)
        auth_token = request.headers.get('Authorization')
        if auth_token != f"Bearer {settings.CRON_SECRET_KEY}":
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        # Exécuter la commande de notifications
        call_command('send_notifications_cron')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notifications envoyées avec succès'
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du déclenchement des notifications: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Vérification de santé du service
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'event-management-notifications'
    })
