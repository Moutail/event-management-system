"""
Vues pour les tâches cron externes
Permet d'appeler les notifications via des requêtes HTTP
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def trigger_notifications(request):
    """
    Déclenche l'envoi des notifications via une requête HTTP
    Utilisé par les services cron externes
    """
    try:
        # Exécuter la commande de notifications en mode silencieux
        from io import StringIO
        import sys
        
        # Capturer la sortie pour éviter les logs excessifs
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            call_command('send_notifications_cron', verbosity=0)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Log minimal
        logger.info("✅ Notifications cron exécutées avec succès")
        
        return JsonResponse({
            'status': 'success',
            'message': 'OK',
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur cron: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal error',
            'timestamp': timezone.now().isoformat()
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

@csrf_exempt
@require_http_methods(["GET"])
def test_cron(request):
    """
    Test simple pour vérifier que le cron fonctionne
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Cron endpoint is working',
        'timestamp': timezone.now().isoformat()
    })
