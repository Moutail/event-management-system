# 🔧 Guide de Dépannage - Système de Streaming

## 🚨 **Problème Actuel : "Sa marche pas"**

Le système de streaming rencontre des erreurs d'authentification avec les APIs YouTube et Zoom.

## 📋 **Diagnostic des Erreurs**

### 1. **Erreur YouTube API**
```
ERROR Erreur HTTP YouTube API: {'error': {'code': 401, 'message': 'API keys are not supported by this API. Expected OAuth2 access token'}}
```
**Cause** : L'API YouTube nécessite OAuth2, pas juste une clé API simple.

### 2. **Erreur Zoom API**
```
ERROR Détails de l'erreur: {'reason': 'Internal Error', 'error': 'invalid_client'}
```
**Cause** : Les identifiants Zoom (Account ID, Client ID, Client Secret) sont incorrects ou expirés.

### 3. **Erreur de Logging Windows**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f50d'
```
**Cause** : Les emojis dans les logs ne sont pas supportés par Windows.

## ✅ **Solutions Appliquées**

### 1. **Services Désactivés Temporairement**
- YouTube et Zoom sont désactivés pour éviter les erreurs
- Le système fonctionne en mode dégradé avec des statuts simulés

### 2. **Gestion d'Erreurs Améliorée**
- Les erreurs d'API sont capturées et gérées gracieusement
- Des statuts par défaut sont retournés quand les services ne sont pas disponibles

### 3. **Configuration Centralisée**
- Fichier `backend/streaming_config.py` pour contrôler les services
- Variables d'environnement pour activer/désactiver les services

## 🚀 **Comment Activer les Services de Streaming**

### **Pour YouTube Live :**

1. **Créer un projet Google Cloud**
   ```bash
   # Aller sur https://console.cloud.google.com
   # Créer un nouveau projet
   ```

2. **Activer l'API YouTube Data v3**
   ```bash
   # Dans la console Google Cloud
   # APIs & Services > Library
   # Rechercher "YouTube Data API v3" et l'activer
   ```

3. **Créer des identifiants OAuth2**
   ```bash
   # APIs & Services > Credentials
   # Create Credentials > OAuth 2.0 Client IDs
   # Configurer l'écran de consentement OAuth
   ```

4. **Modifier `backend/streaming_config.py`**
   ```python
   YOUTUBE_STREAMING_ENABLED = True
   YOUTUBE_API_KEY = "votre_clé_oauth2_ici"
   YOUTUBE_CHANNEL_ID = "votre_id_chaîne_ici"
   ```

### **Pour Zoom :**

1. **Créer une app JWT dans Zoom Marketplace**
   ```bash
   # Aller sur https://marketplace.zoom.us/
   # Sign in > Develop > Build App
   # Choose JWT app type
   ```

2. **Obtenir les identifiants**
   ```bash
   # Account ID, Client ID, Client Secret
   # Sont affichés dans la configuration de l'app
   ```

3. **Modifier `backend/streaming_config.py`**
   ```python
   ZOOM_STREAMING_ENABLED = True
   ZOOM_ACCOUNT_ID = "votre_account_id"
   ZOOM_CLIENT_ID = "votre_client_id"
   ZOOM_CLIENT_SECRET = "votre_client_secret"
   ```

## 🔄 **Redémarrage Requis**

Après modification de la configuration :
```bash
cd backend
python manage.py runserver 8001
```

## 📱 **État Actuel du Système**

### ✅ **Fonctionnel :**
- Interface utilisateur complète
- Gestion des événements virtuels
- Inscriptions et confirmations
- Emails de confirmation

### ⚠️ **Mode Dégradé :**
- Statuts de streaming simulés
- Boutons "Lancer le Stream" affichés mais non fonctionnels
- Section "Rejoindre le Live" avec message "En attente"

### ❌ **Non Fonctionnel :**
- Lancement réel des streams YouTube/Zoom
- Monitoring en temps réel des streams
- Enregistrement automatique

## 🎯 **Prochaines Étapes**

1. **Configurer YouTube OAuth2** (recommandé pour commencer)
2. **Configurer Zoom JWT** (si nécessaire)
3. **Tester avec un événement virtuel simple**
4. **Activer progressivement les fonctionnalités**

## 📞 **Support**

Si vous avez besoin d'aide pour configurer les APIs :
- Consultez la documentation officielle YouTube/Zoom
- Vérifiez que vos identifiants sont corrects
- Assurez-vous que les APIs sont activées dans vos comptes

---

**Note** : Le système est maintenant stable et ne génère plus d'erreurs. Les fonctionnalités de streaming peuvent être activées progressivement en configurant les APIs appropriées.
