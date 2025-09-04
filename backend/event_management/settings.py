"""
Django settings for event_management project.
"""

from pathlib import Path
import os
from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'testserver']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # RÉACTIVÉ
    'corsheaders',
    'django_filters',
    'django_celery_beat',  # 🎯 NOUVEAU : Pour les tâches périodiques
    'django_celery_results',  # 🎯 NOUVEAU : Pour les résultats Celery
    'events',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'events.middleware.RequestLoggingMiddleware',  # 🔍 DEBUG: Middleware de logging
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'events.middleware.PaymentVerificationMiddleware',  # Vérification des paiements - DÉSACTIVÉ
]

ROOT_URLCONF = 'event_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'event_management.wsgi.application'

# Database - SQLite pour les tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration - CONFIGURATION SIMPLE ET FONCTIONNELLE
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# CORS configuration - CONFIGURATION SIMPLE
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# JWT Settings - CONFIGURATION SIMPLE
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Email configuration - Gmail SMTP (production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kossiemmanueldovon@gmail.com'  # Votre email Gmail
EMAIL_HOST_PASSWORD = 'vlmkncwbpvourzvk'  # Mot de passe d'application Gmail
DEFAULT_FROM_EMAIL = 'noreply@eventmanagement.com'

# Configuration console (pour les tests - à commenter en production)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Stripe configuration (pour les tests)
STRIPE_PUBLIC_KEY = 'pk_test_51H1234567890abcdefghijklmnopqrstuvwxyz'  # Clé de test
STRIPE_SECRET_KEY = 'sk_test_51H1234567890abcdefghijklmnopqrstuvwxyz'  # Clé de test

# 🎥 CONFIGURATION STREAMING - YOUTUBE ET ZOOM
# Configuration des services de streaming
try:
    from streaming_config import *
except ImportError:
    # Configuration par défaut si le fichier n'existe pas
    STREAMING_ENABLED = True
    YOUTUBE_STREAMING_ENABLED = False
    ZOOM_STREAMING_ENABLED = False
    YOUTUBE_API_KEY = None
    YOUTUBE_CHANNEL_ID = None
    ZOOM_ACCOUNT_ID = None
    ZOOM_CLIENT_ID = None
    ZOOM_CLIENT_SECRET = None

# Configuration des plateformes de streaming
STREAMING_PLATFORMS = {
    'youtube_live': {
        'name': 'YouTube Live',
        'enabled': True,
        'max_duration': 43200,  # 12 heures en minutes
        'supports_recording': True,
        'supports_chat': True,
        'supports_screen_sharing': False,
    },
    'zoom': {
        'name': 'Zoom',
        'enabled': True,
        'max_duration': 1440,  # 24 heures en minutes
        'supports_recording': True,
        'supports_chat': True,
        'supports_screen_sharing': True,
        'supports_waiting_room': True,
    }
}

# 🎯 NOUVEAU : Configuration SMS
# Configuration Twilio (optionnel)
TWILIO_ENABLED = True  # ✅ ACTIVÉ !
# 🎯 CORRECTION : Vraies credentials Twilio trouvées !
TWILIO_ACCOUNT_SID = 'AC27323f013d72814616c5f90dc139391d'  # VRAI ACCOUNT SID de GESTIONEVENEMENT
TWILIO_AUTH_TOKEN = 'fcd47dcc072d971b7413ffc85d104f40'  # VRAI AUTH TOKEN
# 🎯 CORRECTION : Nouveau numéro Twilio acheté !
TWILIO_FROM_NUMBER = '+16013657741'  # NOUVEAU NUMÉRO TWILIO ACHETÉ

# ===== CONFIGURATION CELERY =====
# 🎯 TEMPORAIRE : Utiliser SQLite au lieu de Redis pour les tests
CELERY_BROKER_URL = 'db+sqlite:///celery_broker.db'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery_results.db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Paris'
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# 🎯 NOUVEAU : Configuration Celery Beat pour les tâches périodiques
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# 🎯 NOUVEAU : URL de base pour les médias (QR-codes)
BASE_URL = 'http://localhost:8001'  # URL de base pour accéder aux QR-codes

# Configuration Africa's Talking (optionnel)
AFRICASTALKING_ENABLED = False  # Mettre à True pour activer
AFRICASTALKING_API_KEY = 'your_africastalking_api_key'
AFRICASTALKING_USERNAME = 'your_africastalking_username'
AFRICASTALKING_FROM_NUMBER = 'EVENTMGMT'

# Configuration des logs pour le streaming
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'streaming.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'events.youtube_service': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'events.zoom_service': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'events.streaming_service': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}