#!/usr/bin/env python
"""
🔐 Configuration pour l'authentification sociale
"""

import os
from decouple import config

# Configuration Google OAuth2
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='your-google-client-id')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='your-google-client-secret')
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='http://localhost:3000/auth/google/callback')

# Configuration Facebook OAuth2
FACEBOOK_APP_ID = config('FACEBOOK_APP_ID', default='your-facebook-app-id')
FACEBOOK_APP_SECRET = config('FACEBOOK_APP_SECRET', default='your-facebook-app-secret')
FACEBOOK_REDIRECT_URI = config('FACEBOOK_REDIRECT_URI', default='http://localhost:3000/auth/facebook/callback')

# Configuration générale
SOCIAL_AUTH_ENABLED = config('SOCIAL_AUTH_ENABLED', default=True, cast=bool)
SOCIAL_AUTH_PROVIDERS = ['google', 'facebook']  # Providers activés

# URLs de redirection après authentification
SOCIAL_AUTH_SUCCESS_URL = config('SOCIAL_AUTH_SUCCESS_URL', default='/dashboard')
SOCIAL_AUTH_FAILURE_URL = config('SOCIAL_AUTH_FAILURE_URL', default='/login?error=social_auth_failed')

# Configuration des scopes OAuth
GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

FACEBOOK_SCOPES = [
    'email',
    'public_profile'
]

# Configuration des permissions par défaut
DEFAULT_SOCIAL_USER_ROLE = 'participant'
DEFAULT_SOCIAL_USER_STATUS = 'approved'

# Configuration de sécurité
SOCIAL_AUTH_TOKEN_EXPIRY = 3600  # 1 heure en secondes
SOCIAL_AUTH_REFRESH_TOKEN_EXPIRY = 2592000  # 30 jours en secondes

# Configuration des avatars par défaut
DEFAULT_AVATAR_URL = 'https://via.placeholder.com/150x150/1976d2/ffffff?text=U'

# Messages d'erreur personnalisés
SOCIAL_AUTH_ERROR_MESSAGES = {
    'google': {
        'invalid_token': 'Token Google invalide. Veuillez réessayer.',
        'network_error': 'Erreur de connexion avec Google. Vérifiez votre connexion internet.',
        'permission_denied': 'Permission refusée par Google. Veuillez autoriser l\'accès.',
    },
    'facebook': {
        'invalid_token': 'Token Facebook invalide. Veuillez réessayer.',
        'network_error': 'Erreur de connexion avec Facebook. Vérifiez votre connexion internet.',
        'permission_denied': 'Permission refusée par Facebook. Veuillez autoriser l\'accès.',
    }
}

# Configuration des webhooks (pour Facebook)
FACEBOOK_WEBHOOK_VERIFY_TOKEN = config('FACEBOOK_WEBHOOK_VERIFY_TOKEN', default='your-webhook-verify-token')

# Configuration des tests
SOCIAL_AUTH_TEST_MODE = config('SOCIAL_AUTH_TEST_MODE', default=False, cast=bool)
SOCIAL_AUTH_TEST_TOKENS = {
    'google': 'test-google-token',
    'facebook': 'test-facebook-token'
}





