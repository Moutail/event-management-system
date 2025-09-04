"""
Configuration des services de streaming
Ce fichier permet de contrôler quels services de streaming sont activés
"""

# Configuration des services de streaming
# Définir à True pour activer, False pour désactiver

# Service de streaming global
STREAMING_ENABLED = True

# Service YouTube Live
# Note: Nécessite une configuration OAuth2 complète
YOUTUBE_STREAMING_ENABLED = False
YOUTUBE_API_KEY = None  # À configurer avec votre clé API
YOUTUBE_CHANNEL_ID = None  # À configurer avec votre ID de chaîne

# Service Zoom
# Note: Nécessite une configuration JWT complète
ZOOM_STREAMING_ENABLED = False
ZOOM_ACCOUNT_ID = None  # À configurer avec votre Account ID
ZOOM_CLIENT_ID = None  # À configurer avec votre Client ID
ZOOM_CLIENT_SECRET = None  # À configurer avec votre Client Secret

# Instructions d'activation :
#
# Pour YouTube :
# 1. Créer un projet Google Cloud
# 2. Activer l'API YouTube Data v3
# 3. Créer des identifiants OAuth2 (pas juste une clé API)
# 4. Configurer l'écran de consentement OAuth
# 5. Définir YOUTUBE_STREAMING_ENABLED = True
# 6. Configurer YOUTUBE_API_KEY et YOUTUBE_CHANNEL_ID
#
# Pour Zoom :
# 1. Créer une app JWT dans le Zoom Marketplace
# 2. Obtenir Account ID, Client ID et Client Secret
# 3. Définir ZOOM_STREAMING_ENABLED = True
# 4. Configurer les variables ZOOM_*
#
# Pour l'instant, les services sont désactivés pour éviter les erreurs
# Le système fonctionnera en mode dégradé avec des statuts simulés
