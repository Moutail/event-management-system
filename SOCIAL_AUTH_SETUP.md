# 🔐 Guide d'installation de l'authentification sociale

## 🚀 Vue d'ensemble

Ce guide vous explique comment configurer l'authentification sociale avec **Google** et **Facebook** dans votre système de gestion d'événements.

## 📋 Prérequis

- Python 3.8+
- Node.js 16+
- Comptes développeur Google et Facebook
- Accès aux consoles de développement Google et Facebook

## 🔧 Configuration Backend

### 1. Installation des dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuration des variables d'environnement

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Facebook OAuth2
FACEBOOK_APP_ID=your-facebook-app-id-here
FACEBOOK_APP_SECRET=your-facebook-app-secret-here
FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback

# Configuration générale
SOCIAL_AUTH_ENABLED=True
SOCIAL_AUTH_SUCCESS_URL=/dashboard
SOCIAL_AUTH_FAILURE_URL=/login?error=social_auth_failed
```

### 3. Configuration Google OAuth2

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un existant
3. Activez l'API Google+ API
4. Allez dans "Identifiants" > "Créer des identifiants" > "ID client OAuth 2.0"
5. Configurez les URIs de redirection autorisés :
   - `http://localhost:3000/auth/google/callback` (développement)
   - `https://votre-domaine.com/auth/google/callback` (production)
6. Copiez le `Client ID` et `Client Secret`

### 4. Configuration Facebook OAuth2

1. Allez sur [Facebook Developers](https://developers.facebook.com/)
2. Créez une nouvelle application
3. Ajoutez le produit "Facebook Login"
4. Configurez les URIs de redirection OAuth valides :
   - `http://localhost:3000/auth/facebook/callback` (développement)
   - `https://votre-domaine.com/auth/facebook/callback` (production)
5. Copiez l'`App ID` et l'`App Secret`

### 5. Migration de la base de données

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## 🔧 Configuration Frontend

### 1. Installation des dépendances

```bash
cd frontend
npm install
```

### 2. Configuration des variables d'environnement

Créez un fichier `.env` dans le dossier `frontend/` :

```env
# Google OAuth2
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id-here
REACT_APP_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Facebook OAuth2
REACT_APP_FACEBOOK_APP_ID=your-facebook-app-id-here
REACT_APP_FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback

# Configuration générale
REACT_APP_SOCIAL_AUTH_ENABLED=true
REACT_APP_SOCIAL_AUTH_SUCCESS_URL=/dashboard
REACT_APP_SOCIAL_AUTH_FAILURE_URL=/login?error=social_auth_failed
```

## 🧪 Test de l'authentification

### 1. Démarrer le backend

```bash
cd backend
python manage.py runserver 8001
```

### 2. Démarrer le frontend

```bash
cd frontend
npm start
```

### 3. Tester l'authentification

1. Allez sur `http://localhost:3000/login`
2. Cliquez sur "Continuer avec Google" ou "Continuer avec Facebook"
3. Suivez le processus d'authentification
4. Vérifiez que vous êtes redirigé vers le bon dashboard

## 🔒 Sécurité

### Bonnes pratiques

- ✅ Utilisez HTTPS en production
- ✅ Validez toujours les tokens côté serveur
- ✅ Implémentez la protection CSRF avec le paramètre `state`
- ✅ Limitez les scopes OAuth au minimum nécessaire
- ✅ Stockez les tokens de manière sécurisée
- ✅ Implémentez la révocation des tokens

### Protection CSRF

Le système utilise un paramètre `state` aléatoire pour protéger contre les attaques CSRF :

```javascript
state: Math.random().toString(36).substring(7)
```

## 🚨 Dépannage

### Erreurs courantes

1. **"Client ID invalide"**
   - Vérifiez que le CLIENT_ID est correct
   - Vérifiez que l'URI de redirection est autorisé

2. **"URI de redirection non autorisé"**
   - Ajoutez l'URI dans la console Google/Facebook
   - Vérifiez qu'il n'y a pas d'espaces en trop

3. **"Erreur de réseau"**
   - Vérifiez votre connexion internet
   - Vérifiez que les APIs sont activées

4. **"Token expiré"**
   - Implémentez le rafraîchissement automatique des tokens
   - Vérifiez la configuration des délais d'expiration

### Logs de débogage

Activez les logs détaillés en ajoutant dans `.env` :

```env
DEBUG=True
SOCIAL_AUTH_DEBUG=True
```

## 📱 Intégration mobile

Pour l'intégration mobile, utilisez les SDKs officiels :

- **Google** : [Google Sign-In SDK](https://developers.google.com/identity/sign-in/android)
- **Facebook** : [Facebook Login SDK](https://developers.facebook.com/docs/facebook-login/android)

## 🌐 Déploiement en production

### 1. Mise à jour des URIs de redirection

```env
GOOGLE_REDIRECT_URI=https://votre-domaine.com/auth/google/callback
FACEBOOK_REDIRECT_URI=https://votre-domaine.com/auth/facebook/callback
```

### 2. Configuration HTTPS

- Installez un certificat SSL
- Forcez HTTPS dans votre application
- Mettez à jour les URIs de redirection

### 3. Variables d'environnement

- Utilisez des gestionnaires de secrets (AWS Secrets Manager, Azure Key Vault, etc.)
- Ne committez jamais les clés secrètes dans le code
- Utilisez des variables d'environnement sécurisées

## 📚 Ressources supplémentaires

- [Documentation Google OAuth2](https://developers.google.com/identity/protocols/oauth2)
- [Documentation Facebook OAuth2](https://developers.facebook.com/docs/facebook-login)
- [Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/)
- [React OAuth2](https://github.com/azmenak/react-oauth2)

## 🆘 Support

En cas de problème :

1. Vérifiez les logs du serveur
2. Vérifiez la console du navigateur
3. Vérifiez la configuration des variables d'environnement
4. Testez avec les comptes de développement

---

**🎉 Félicitations !** Votre système d'authentification sociale est maintenant configuré et prêt à être utilisé !









