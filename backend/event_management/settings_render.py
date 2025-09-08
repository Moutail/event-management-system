"""
Configuration optimisée pour Render (sans services payants)
Utilise des tâches intégrées au lieu de Celery
"""

import os
from .settings import *

# Configuration de base pour Render
DEBUG = False
ALLOWED_HOSTS = [
    'event-management-backend.onrender.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0'
]

# Configuration de la base de données MySQL pour le déploiement
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuration des fichiers statiques pour Render
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuration des médias
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuration CORS pour la production
CORS_ALLOWED_ORIGINS = [
    "https://event-management-frontend.vercel.app",
    "https://event-management-frontend-git-main.vercel.app",
    "https://event-management-frontend-git-develop.vercel.app",
]

# Configuration simplifiée sans Celery (pour Render gratuit)
# Utilise des tâches intégrées au lieu de Celery
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'django-db'

# Configuration des logs pour la production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'events': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuration de sécurité pour la production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuration des sessions
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuration de l'URL de base pour les médias
BASE_URL = os.environ.get('BASE_URL', 'https://event-management-backend.onrender.com')

# Configuration des emails (utilise les variables d'environnement)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@eventmanagement.com')

# Configuration Stripe (utilise les variables d'environnement)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

# Configuration Twilio (utilise les variables d'environnement)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')

# Configuration OAuth2 (utilise les variables d'environnement)
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
FACEBOOK_OAUTH2_CLIENT_ID = os.environ.get('FACEBOOK_OAUTH2_CLIENT_ID')
FACEBOOK_OAUTH2_CLIENT_SECRET = os.environ.get('FACEBOOK_OAUTH2_CLIENT_SECRET')

# Configuration des services de streaming
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
ZOOM_ACCOUNT_ID = os.environ.get('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET')
